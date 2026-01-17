"""
Командный интерфейс приложения
"""

import shlex
from datetime import datetime
from typing import Optional

from prettytable import PrettyTable
from valutatrade_hub.core.models import User
from valutatrade_hub.core.usecases import PortfolioManager, UserManager
from valutatrade_hub.core.utils import DataManager, ExchangeRateService


class CLIInterface:
    """Интерфейс командной строки"""

    def __init__(self):
        self.data_manager = DataManager()
        self.rate_service = ExchangeRateService(self.data_manager)
        self.user_manager = UserManager(self.data_manager)
        self.portfolio_manager = PortfolioManager(self.data_manager, self.rate_service)
        self.current_user: Optional[User] = None

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
        """Вход в систему."""
        try:
            self.current_user = self.user_manager.login(username, password)
            print(f"Вы вошли как '{self.current_user.username}'")
        except ValueError as e:
            print(f"Ошибка: {e}")

    def show_portfolio(self, base_currency: str = "USD") -> None:
        """Показывает портфель пользователя."""
        if not self.current_user:
            print("Ошибка: Сначала выполните login")
            return

        try:
            portfolio = self.portfolio_manager.get_user_portfolio(
                self.current_user.user_id
            )
            base_currency = base_currency.upper()

            print(
                f"\nПортфель пользователя '{self.current_user.username}'\
                (база: {base_currency}):"
            )

            if not portfolio.wallets:
                print("  Портфель пуст")
                return

            # Используем PrettyTable для красивого вывода
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
                    rate = self.rate_service.get_rate(currency_code, base_currency)
                    if rate:
                        value = balance * rate
                    else:
                        value = 0
                        rate = "N/A"

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

            print(f"\nПокупка выполнена: {result['amount']:.4f} {result['currency']}")

            if result["rate"]:
                print(f"По курсу: {result['rate']:.2f} USD/{result['currency']}")
                if result["estimated_cost"]:
                    print(f"Оценочная стоимость: {result['estimated_cost']:,.2f} USD")

            print("Изменения в портфеле:")
            print(
                f"  - {result['currency']}: было {result['old_balance']:.4f}"
                    f"стало {result['new_balance']:.4f}"
            )

        except ValueError as e:
            print(f"Ошибка: {e}")

    def sell(self, currency: str, amount: float) -> None:
        """Продажа валюты."""
        if not self.current_user:
            print("Ошибка: Сначала выполните login")
            return

        try:
            result = self.portfolio_manager.sell_currency(
                self.current_user.user_id, currency, amount
            )

            print(f"\nПродажа выполнена: {result['amount']:.4f} {result['currency']}")

            if result["rate"]:
                print(f"По курсу: {result['rate']:.2f} USD/{result['currency']}")
                if result["estimated_revenue"]:
                    print(f"Оценочная выручка: {result['estimated_revenue']:,.2f} USD")

            print("Изменения в портфеле:")
            print(
                f"  - {result['currency']}: было {result['old_balance']:.4f}"
                f" - стало {result['new_balance']:.4f}"
            )

        except ValueError as e:
            print(f"Ошибка: {e}")

    def get_rate(self, from_currency: str, to_currency: str) -> None:
        """Получение курса валюты"""
        try:
            rate = self.rate_service.get_rate(from_currency, to_currency)

            if rate:
                rates = self.rate_service.get_rates()
                updated_at = rates.get("last_refresh", "неизвестно")

                print(f"Курс {from_currency.upper()} - {to_currency.upper()}:"
                        f" {rate:.6f}")
                print(f"Обновлено: {updated_at}")

                if rate != 0:
                    reverse_rate = 1.0 / rate
                    print(
                        f"Обратный курс {to_currency.upper()}"
                        f"- {from_currency.upper()}: {reverse_rate:.6f}"
                    )
            else:
                print(f"Курс {from_currency.upper()} - {to_currency.upper()}"
                    f" недоступен.")

        except Exception as e:
            print(f"Ошибка при получении курса: {e}")

    def _print_help(self) -> None:
        """Выводит справку по командам"""
        print("\nДоступные команды:")
        print("  register --username <имя> --password <пароль>")
        print("  login --username <имя> --password <пароль>")
        print("  show-portfolio [--base <валюта>]")
        print("  buy --currency <код> --amount <сумма>")
        print("  sell --currency <код> --amount <сумма>")
        print("  get-rate --from <валюта> --to <валюта>")
        print("  update-rates")
        print("  help")
        print("  exit")
        print("\nПримеры:")
        print("  register --username Иван --password 7890")
        print("  buy --currency USD --amount 200")
        print("  get-rate --from USD --to BTC")
        print("  show-portfolio")
        print("  show-portfolio --base USD")

    def update_rates(self) -> None:
        """Обновляет курсы валют."""
        try:
            # Демонстрационные курсы
            demo_rates = {
                "pairs": {
                    "BTC_USD": {
                        "rate": 59337.21,
                        "source": "demo",
                        "updated_at": datetime.now().isoformat(),
                    },
                    "EUR_USD": {
                        "rate": 1.0786,
                        "source": "demo",
                        "updated_at": datetime.now().isoformat(),
                    },
                    "RUB_USD": {
                        "rate": 0.01016,
                        "source": "demo",
                        "updated_at": datetime.now().isoformat(),
                    },
                    "ETH_USD": {
                        "rate": 3720.00,
                        "source": "demo",
                        "updated_at": datetime.now().isoformat(),
                    },
                }
            }

            self.rate_service.update_rates(demo_rates)
            print("Курсы обновлены успешно!")

        except Exception as e:
            print(f"Ошибка при обновлении курсов: {e}")

    def _parse_command(self, user_input: str) -> tuple:
        """Парсит введенную команду"""
        try:
            parts = shlex.split(user_input)
            if not parts:
                return None, None

            command = parts[0]
            args = {}

            # Парсим аргументы
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

        # Импортируем datetime здесь, чтобы избежать циклического импорта

        while True:
            try:
                # Создаем промпт с именем пользователя, если он авторизован
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

                # Парсим команду
                command, args = self._parse_command(user_input)

                if not command:
                    print("Неизвестная команда. Введите 'help' для справки.")
                    continue

                # Выполняем команду
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

                elif command == "update-rates":
                    self.update_rates()

                else:
                    print(f"Неизвестная команда: {command}")
                    print("Введите 'help' для списка команд")

            except KeyboardInterrupt:
                print("\n\nДо свидания!")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
