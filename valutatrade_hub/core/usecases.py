"""
Бизнес-логика приложения
"""

import secrets
from datetime import datetime
from typing import Dict, Optional

from ..decorators import log_action
from ..infra.settings import SettingsLoader
from ..infra.database import DatabaseManager
from .currencies import get_currency
from .exceptions import ApiRequestError, CurrencyNotFoundError, InsufficientFundsError
from .models import Portfolio, User


class UserManager:
    """Менеджер пользователей"""

    def __init__(self):
        self.db = DatabaseManager()
        self.current_user: Optional[User] = None

    @log_action("REGISTER")
    def register_user(self, username: str, password: str) -> User:
        """Регистрирует нового пользователя."""
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")

        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")

        users_data = self.db.load("users.json", [])

        # Проверка уникальности имени
        for user in users_data:
            if user["username"] == username:
                raise ValueError(f"Имя пользователя '{username}' уже занято")

        # Создание пользователя
        user_id = self.db.get_next_user_id()
        salt = secrets.token_hex(8)
        hashed_password = self._hash_password(password, salt)
        registration_date = datetime.now()

        user = User(user_id, username, hashed_password, salt, registration_date)

        # Сохранение
        users_data.append(user.to_dict())
        self.db.save("users.json", users_data)

        # Создание пустого портфеля
        self._create_user_portfolio(user_id)

        return user

    @log_action("LOGIN")
    def login(self, username: str, password: str) -> User:
        """Аутентификация пользователя"""
        users_data = self.db.load("users.json", [])

        for user_data in users_data:
            if user_data["username"] == username:
                user = User.from_dict(user_data)
                if user.verify_password(password):
                    self.current_user = user
                    return user
                else:
                    raise ValueError("Неверный пароль")

        raise ValueError(f"Пользователь '{username}' не найден")

    def logout(self) -> None:
        """Выход из системы."""
        self.current_user = None

    def _create_user_portfolio(self, user_id: int) -> None:
        """Создает пустой портфель для пользователя."""
        portfolios_data = self.db.load("portfolios.json", [])

        # Проверяем, не существует ли уже портфель
        for portfolio in portfolios_data:
            if portfolio["user_id"] == user_id:
                return

        # Создаем новый портфель
        portfolio = Portfolio(user_id)
        portfolios_data.append(portfolio.to_dict())
        self.db.save("portfolios.json", portfolios_data)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Хеширует пароль."""
        import hashlib

        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


class PortfolioManager:
    """Менеджер портфелей"""

    def __init__(self):
        self.db = DatabaseManager()
        self.settings = SettingsLoader()

    def get_user_portfolio(self, user_id: int) -> Portfolio:
        """Получает портфель пользователя."""
        portfolios_data = self.db.load("portfolios.json", [])

        for portfolio_data in portfolios_data:
            if portfolio_data["user_id"] == user_id:
                return Portfolio.from_dict(portfolio_data)

        # Если портфель не найден, создаем новый
        portfolio = Portfolio(user_id)
        self._save_portfolio(portfolio)
        return portfolio

    @log_action("BUY", verbose=True)
    def buy_currency(self, user_id: int, currency_code: str, amount: float) -> Dict:
        """Покупка валюты."""
        if not self._validate_amount(amount):
            raise ValueError("Сумма должна быть положительной")

        try:
            currency = get_currency(currency_code)
        except CurrencyNotFoundError as e:
            raise e

        portfolio = self.get_user_portfolio(user_id)
        currency_code = currency_code.upper()

        # Добавляем валюту, если её нет
        if currency_code not in portfolio.wallets:
            portfolio.add_currency(currency_code)

        wallet = portfolio.get_wallet(currency_code)
        old_balance = wallet.balance
        wallet.deposit(amount)

        self._save_portfolio(portfolio)

        # Рассчитываем стоимость
        rate = self._get_rate_with_fallback(currency_code, "USD")
        estimated_cost = amount * rate if rate else None

        return {
            "currency": currency_code,
            "currency_name": currency.name,
            "amount": amount,
            "rate": rate,
            "estimated_cost": estimated_cost,
            "old_balance": old_balance,
            "new_balance": wallet.balance,
        }

    @log_action("SELL", verbose=True)
    def sell_currency(self, user_id: int, currency_code: str, amount: float) -> Dict:
        """Продажа валюты."""
        if not self._validate_amount(amount):
            raise ValueError("Сумма должна быть положительной")

        try:
            currency = get_currency(currency_code)
        except CurrencyNotFoundError as e:
            raise e

        portfolio = self.get_user_portfolio(user_id)
        currency_code = currency_code.upper()

        wallet = portfolio.get_wallet(currency_code)
        if not wallet:
            raise ValueError(f"У вас нет кошелька для валюты '{currency_code}'")

        old_balance = wallet.balance

        try:
            wallet.withdraw(amount)
        except InsufficientFundsError as e:
            raise e

        self._save_portfolio(portfolio)

        # Рассчитываем выручку
        rate = self._get_rate_with_fallback(currency_code, "USD")
        estimated_revenue = amount * rate if rate else None

        return {
            "currency": currency_code,
            "currency_name": currency.name,
            "amount": amount,
            "rate": rate,
            "estimated_revenue": estimated_revenue,
            "old_balance": old_balance,
            "new_balance": wallet.balance,
        }

    def _save_portfolio(self, portfolio: Portfolio) -> None:
        """Сохраняет портфель"""
        portfolios_data = self.db.load("portfolios.json", [])

        found = False
        for i, portfolio_data in enumerate(portfolios_data):
            if portfolio_data["user_id"] == portfolio.user_id:
                portfolios_data[i] = portfolio.to_dict()
                found = True
                break

        if not found:
            portfolios_data.append(portfolio.to_dict())

        self.db.save("portfolios.json", portfolios_data)

    def _get_rate_with_fallback(
        self, from_currency: str, to_currency: str
    ) -> Optional[float]:
        """Получает курс с обработкой ошибок"""
        try:
            # Здесь в будущем будет реальный сервис курсов
            demo_rates = {
                "BTC_USD": 59337.21,
                "EUR_USD": 1.0786,
                "RUB_USD": 0.01016,
                "ETH_USD": 3720.00,
                "USD_USD": 1.0,
            }

            rate_key = f"{from_currency}_{to_currency}"
            if rate_key in demo_rates:
                return demo_rates[rate_key]

            reverse_key = f"{to_currency}_{from_currency}"
            if reverse_key in demo_rates:
                return 1.0 / demo_rates[reverse_key]

            return None

        except Exception as e:
            raise ApiRequestError(str(e))

    @staticmethod
    def _validate_currency_code(currency_code: str) -> bool:
        """Проверяет валидность кода валюты"""
        return (
            isinstance(currency_code, str)
            and len(currency_code) >= 2
            and len(currency_code) <= 5
            and currency_code.isalpha()
        )

    @staticmethod
    def _validate_amount(amount: float) -> bool:
        """Проверяет валидность суммы"""
        return isinstance(amount, (int, float)) and amount > 0
