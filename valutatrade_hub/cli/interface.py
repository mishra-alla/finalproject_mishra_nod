# В valutatrade_hub/cli/interface.py
"""
Командный интерфейс приложения.
"""

import shlex
from datetime import datetime
from typing import Optional

from prettytable import PrettyTable
from valutatrade_hub.core.currencies import get_all_currencies
from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.models import User
from valutatrade_hub.core.usecases import PortfolioManager, UserManager

from valutatrade_hub.parser_service.updater import RatesUpdater
from valutatrade_hub.parser_service.storage import RatesStorage
from valutatrade_hub.parser_service.config import ParserConfig
# from valutatrade_hub.parser_service.scheduler import RatesScheduler


class CLIInterface:
    """Интерфейс командной строки"""

    def __init__(self):
        self.user_manager = UserManager()
        self.portfolio_manager = PortfolioManager()
        self.current_user: Optional[User] = None
        # Инициализация парсера
        self.rates_updater = RatesUpdater()
        self.rates_storage = RatesStorage(ParserConfig())

    def register(self, username: str, password: str) -> None:
        """Регистрация нового пользователя."""
        try:
            user = self.user_manager.register_user(username, password)
            print(
                f"Пользователь '{user.username}' зарегистрирован (id={user.user_id})."
            )
            print(f"Войдите: login --username {user.username} --password ****")
        except ValueError as e:
            print(f"Ошибка: {e}")

    def login(self, username: str, password: str) -> None:
        """Вход в систему"""
        try:
            self.current_user = self.user_manager.login(username, password)
            print(f"Вы вошли как '{self.current_user.username}'")
        except ValueError as e:
            print(f"Ошибка: {e}")

    def show_portfolio(self, base_currency: str = "USD") -> None:
        """Показывает портфель пользователя"""
        if not self.current_user:
            print("Ошибка: Сначала выполните login")
            return

        try:
            portfolio = self.portfolio_manager.get_user_portfolio(
                self.current_user.user_id
            )
            base_currency = base_currency.upper()

            print(
                f"\nПортфель пользователя '{self.current_user.username}'"
                f"(база: {base_currency}):"
            )

            if not portfolio.wallets:
                print("  Портфель пуст")
                return

            table = PrettyTable()
            table.field_names = ["Валюта", "Баланс", f"В {base_currency}", "Курс"]
            table.align["Валюта"] = "l"
            table.align["Баланс"] = "r"
            table.align[f"В {base_currency}"] = "r"
            table.align["Курс"] = "r"

            total_value = 0.0

            for currency_code, wallet in portfolio.wallets.items():
                balance = wallet.balance

                if currency_code == base_currency:
                    value = balance
                    rate = 1.0
                else:
                    try:
                        rate = self.portfolio_manager._get_rate_with_fallback(
                            currency_code, base_currency
                        )
                        if rate:
                            value = balance * rate
                        else:
                            value = 0
                            rate = "N/A"
                    except ApiRequestError:
                        value = 0
                        rate = "API Error"

                table.add_row(
                    [
                        currency_code,
                        f"{balance:.4f}",
                        f"{value:.2f}" if isinstance(value, (int, float)) else "N/A",
                        f"{rate:.4f}" if isinstance(rate, (int, float)) else rate,
                    ]
                )

                if isinstance(value, (int, float)):
                    total_value += value

            print(table)
            print(f"\nИТОГО: {total_value:,.2f} {base_currency}")

        except Exception as e:
            print(f"Ошибка при получении портфеля: {e}")

    def buy(self, currency: str, amount: float) -> None:
        """Покупка валюты"""
        if not self.current_user:
            print("Ошибка: Сначала выполните login")
            return

        try:
            result = self.portfolio_manager.buy_currency(
                self.current_user.user_id, currency, amount
            )

            print(
                f"\nПокупка выполнена: {result['amount']:.4f}"
                f" {result['currency']} ({result['currency_name']})"
            )

            if result["rate"]:
                print(f"По курсу: {result['rate']:.2f} USD/{result['currency']}")
                if result["estimated_cost"]:
                    print(f"Оценочная стоимость: {result['estimated_cost']:,.2f} USD")

            print("Изменения в портфеле:")
            print(
                f"  - {result['currency']}: было {result['old_balance']:.4f} -"
                f" стало {result['new_balance']:.4f}"
            )

        except (CurrencyNotFoundError, ValueError) as e:
            print(f"Ошибка: {e}")
            if isinstance(e, CurrencyNotFoundError):
                print("Используйте 'list-currencies' для списка доступных валют")
        except ApiRequestError as e:
            print(f"Ошибка API: {e}")
            print("Повторите попытку позже")

    def sell(self, currency: str, amount: float) -> None:
        """Продажа валюты."""
        if not self.current_user:
            print("Ошибка: Сначала выполните login")
            return

        try:
            result = self.portfolio_manager.sell_currency(
                self.current_user.user_id, currency, amount
            )

            print(
                f"\nПродажа выполнена: {result['amount']:.4f} "
                f"{result['currency']} ({result['currency_name']})"
            )

            if result["rate"]:
                print(f"По курсу: {result['rate']:.2f} USD/{result['currency']}")
                if result["estimated_revenue"]:
                    print(f"Оценочная выручка: {result['estimated_revenue']:,.2f} USD")

            print("Изменения в портфеле:")
            print(
                f"  - {result['currency']}: было {result['old_balance']:.4f}"
                f" - стало {result['new_balance']:.4f}"
            )

        except (CurrencyNotFoundError, InsufficientFundsError, ValueError) as e:
            print(f"Ошибка: {e}")
            if isinstance(e, CurrencyNotFoundError):
                print("Используйте 'list-currencies' для списка доступных валют")
        except ApiRequestError as e:
            print(f"Ошибка API: {e}")
            print("Повторите попытку позже")

    def get_rate(self, from_currency: str, to_currency: str) -> None:
        """Получение курса валюты"""
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()

            # Валидация валют
            # from_val = from_currency
            # to_val = to_currency

            rate = self.portfolio_manager._get_rate_with_fallback(
                from_currency, to_currency
            )

            if rate:
                print(f"Курс {from_currency} - {to_currency}: {rate:.6f}")
                print(f"Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                if rate != 0:
                    reverse_rate = 1.0 / rate
                    print(
                        f"Обратный курс {to_currency} - {from_currency}:"
                        f" {reverse_rate:.6f}"
                    )
            else:
                print(f"Курс {from_currency} - {to_currency} недоступен.")
                print("Проверьте коды валют или повторите позже")

        except CurrencyNotFoundError as e:
            print(f"Ошибка: {e}")
            print("Используйте 'list-currencies' для списка доступных валют")
        except ApiRequestError as e:
            print(f"Ошибка API: {e}")
            print("Повторите попытку позже или проверьте соединение")
        except Exception as e:
            print(f"Ошибка при получении курса: {e}")

    def update_rates(self, source: Optional[str] = None) -> None:
        """Обновляет курсы валют"""
        # ВАЛИДАЦИЯ источника
        valid_sources = ["coingecko", "exchangerate"]

        if source:
            source = source.lower()
            if source not in valid_sources:
                print(
                    f" Неверный источник: '{source}'."
                    f" Допустимые: {', '.join(valid_sources)}"
                )
                print("Использую все источники")
                source = None

        if source:
            print(f"Обновление курсов (источник: {source})...")
        else:
            print("Обновление курсов (все источники)...")

        # Используем класс RatesUpdater
        rates = self.rates_updater.run_update(source)

        if rates:
            count = len(rates)
            print(f" Обновлено {count} курсов")

            # Показываем несколько примеров
            print("\nПримеры обновленных курсов:")
            displayed = 0
            for pair, data in rates.items():
                if displayed < 3:  # Показываем первые 3
                    print(f"  {pair}: {data['rate']:.4f} ({data.get('source', '?')})")
                    displayed += 1
        else:
            print("Не удалось обновить курсы")

    def show_rates(
        self,
        currency: Optional[str] = None,
        top: Optional[int] = None,
        base: str = "USD",
    ) -> None:
        """Показывает курсы из кэша"""
        # Используем storage
        # data = load_current_rates()
        data = self.rates_storage.load_current_rates()

        if not data.get("pairs"):
            print("Кэш курсов пуст. Запустите 'update-rates'")
            return

        pairs = data["pairs"]
        # Фильтрация
        if currency:
            currency = currency.upper()
            filtered = {
                k: v
                for k, v in pairs.items()
                if k.startswith(f"{currency}_") or k.endswith(f"_{currency}")
            }
        else:
            filtered = pairs
        # Сортировка
        sorted_pairs = sorted(
            filtered.items(), key=lambda x: x[1]["rate"], reverse=True
        )
        # Ограничение
        if top:
            sorted_pairs = sorted_pairs[:top]
        # Вывод
        print(f"Курсы (обновлено: {data.get('last_refresh', 'неизвестно')}):")
        print("-" * 50)

        for pair, info in sorted_pairs:
            print(f"{pair:10} {info['rate']:10.4f} ({info.get('source', '?')})")

        print(f"Всего: {len(sorted_pairs)} курсов")

    def _print_help(self) -> None:
        """Выводит справку по командам"""
        print("\nДоступные команды:")
        print("  register --username <имя> --password <пароль>")
        print("  login --username <имя> --password <пароль>")
        print("  show-portfolio [--base <валюта>]")
        print("  buy --currency <код> --amount <сумма>")
        print("  sell --currency <код> --amount <сумма>")
        print("  get-rate --from <валюта> --to <валюта>")
        print("  update-rates [--source <coingecko|exchangerate>]")
        print("  show-rates [--currency <код>] [--top <N>] [--base <валюта>]")
        print("  list-currencies")
        print("  help")
        print("  exit")
        print("\nПримеры:")
        print("  register --username Иван --password 7890")
        print("  login --username Иван --password 7890")
        print("  buy --currency USD --amount 200")
        print("  get-rate --from USD --to BTC")
        print("  get-rate --from BTC --to RUS")
        print("  sell --currency RUS --amount 1000")
        print("  update-rates --source coingecko")
        print("  show-rates --top 5")
        print("  show-portfolio")
        print("  show-portfolio --base USD")

    def list_currencies(self) -> None:
        """Список поддерживаемых валют"""
        try:
            currencies = get_all_currencies()

            if not currencies:
                print("Нет доступных валют")
                return
            print("\nПоддерживаемые валюты:")
            print("-" * 60)
            for code, currency in currencies.items():
                print(f"  {currency.get_display_info()}")
            print("-" * 60)
            print(f"Всего: {len(currencies)} валют")

        except Exception as e:
            print(f"Ошибка при получении списка валют: {e}")

    def _parse_command(self, user_input: str) -> tuple:
        """Парсит введенную команду"""
        try:
            parts = shlex.split(user_input)
            if not parts:
                return None, None
            command = parts[0]
            args = {}
            i = 1
            while i < len(parts):
                if parts[i].startswith("--"):
                    arg_name = parts[i][2:]
                    if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                        args[arg_name] = parts[i + 1]
                        i += 2
                    else:
                        args[arg_name] = True
                        i += 1
                else:
                    i += 1
            return command, args
        except Exception:
            return None, None

    def run(self) -> None:
        """Запускает интерфейс командной строки"""
        print("\nДобро пожаловать в ValutaTrade Hub!")
        print("Введите 'help' для списка команд или 'exit' для выхода")

        while True:
            try:
                prompt = "valutatrade"
                if self.current_user:
                    prompt = f"valutatrade[{self.current_user.username}]"

                user_input = input(f"\n{prompt}> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "выход"]:
                    print("До свидания!")
                    break

                if user_input.lower() == "help":
                    self._print_help()
                    continue

                command, args = self._parse_command(user_input)

                if not command:
                    print("Неизвестная команда. Введите 'help' для справки.")
                    continue

                if command == "register":
                    if "username" in args and "password" in args:
                        self.register(args["username"], args["password"])
                    else:
                        print("Ошибка: укажите --username и --password")

                elif command == "login":
                    if "username" in args and "password" in args:
                        self.login(args["username"], args["password"])
                    else:
                        print("Ошибка: укажите --username и --password")

                elif command == "show-portfolio":
                    base = args.get("base", "USD")
                    self.show_portfolio(base)

                elif command == "buy":
                    if "currency" in args and "amount" in args:
                        try:
                            amount = float(args["amount"])
                            self.buy(args["currency"], amount)
                        except ValueError:
                            print("Ошибка: amount должен быть числом")
                    else:
                        print("Ошибка: укажите --currency и --amount")

                elif command == "sell":
                    if "currency" in args and "amount" in args:
                        try:
                            amount = float(args["amount"])
                            self.sell(args["currency"], amount)
                        except ValueError:
                            print("Ошибка: amount должен быть числом")
                    else:
                        print("Ошибка: укажите --currency и --amount")

                elif command == "get-rate":
                    if "from" in args and "to" in args:
                        self.get_rate(args["from"], args["to"])
                    else:
                        print("Ошибка: укажите --from и --to")

                elif command == "list-currencies":
                    self.list_currencies()

                elif command == "update-rates":
                    source = args.get("source")
                    self.update_rates(source)

                elif command == "show-rates":
                    currency = args.get("currency")
                    top = int(args.get("top")) if args.get("top") else None
                    base = args.get("base", "USD")
                    self.show_rates(currency, top, base)

                else:
                    print(f"Неизвестная команда: {command}")
                    print("Введите 'help' для списка команд")

            except KeyboardInterrupt:
                print("\n\nДо свидания!")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")


#    def _get_logger(self):
#        """Возвращает логгер."""
#        import logging
#        return logging.getLogger(__name__)
