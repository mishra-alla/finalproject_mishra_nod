"""
Модели данных для системы торговли валютами
"""

import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional


class User:
    """Класс пользователя системы"""

    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime,
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value

    @property
    def hashed_password(self) -> str:
        return self._hashed_password

    @property
    def salt(self) -> str:
        return self._salt

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    def get_user_info(self) -> str:
        """Выводит информацию о пользователе."""
        return (
            f"ID: {self._user_id}, "
            f"Имя: {self._username}, "
            f"Зарегистрирован: {self._registration_date.strftime('%Y-%m-%d')}"
        )

    def change_password(self, new_password: str) -> None:
        """Изменяет пароль пользователя."""
        if len(new_password) < 4:
            raise ValueError("Минимальный размер пароля 4 символа")

        new_salt = secrets.token_hex(8)
        new_hashed_password = self._hash_password(new_password, new_salt)

        self._hashed_password = new_hashed_password
        self._salt = new_salt

    def verify_password(self, password: str) -> bool:
        """Проверяет пароль."""
        test_hash = self._hash_password(password, self._salt)
        return test_hash == self._hashed_password

    def _hash_password(self, password: str, salt: str) -> str:
        """Хеширует пароль с солью"""
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для сохранения"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Создает объект из словаря."""
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=datetime.fromisoformat(data["registration_date"]),
        )


class Wallet:
    """Кошелек пользователя для одной валюты"""

    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code.upper()
        self._balance = float(balance)

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)

    def deposit(self, amount: float) -> None:
        """Пополняет баланс."""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Снимает средства с баланса"""
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self._balance:
            raise ValueError(
                f"Недостаточно средств: доступно {self._balance:.4f},"
                f"требуется {amount:.4f}"
            )
        self.balance -= amount

    def get_balance_info(self) -> str:
        """Возвращает информацию о балансе"""
        return f"{self.currency_code}: {self._balance:.4f}"

    def to_dict(self) -> dict:
        """Преобразует объект в словарь"""
        return {"currency_code": self.currency_code, "balance": self._balance}

    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        """Создает объект из словаря"""
        return cls(currency_code=data["currency_code"], balance=data["balance"])


class Portfolio:
    """Портфель пользователя со всеми кошельками"""

    def __init__(self, user_id: int, wallets: Optional[Dict[str, Wallet]] = None):
        self._user_id = user_id
        self._wallets = wallets or {}

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        return self._wallets.copy()

    def add_currency(self, currency_code: str) -> None:
        """Добавляет новый кошелек"""
        currency_code = currency_code.upper()
        if currency_code in self._wallets:
            raise ValueError(f"Кошелек для валюты '{currency_code}' уже существует")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        """Возвращает кошелек по коду валюты."""
        currency_code = currency_code.upper()
        return self._wallets.get(currency_code)

    def get_total_value(self, base_currency: str = "USD") -> float:
        """Рассчитывает общую стоимость портфеля в базовой валюте."""
        total_value = 0.0

        # Фиксированные курсы валют для демонстрации
        demo_rates = {
            "BTC_USD": 59337.21,
            "EUR_USD": 1.0786,
            "RUB_USD": 0.01016,
            "ETH_USD": 3720.00,
            "USD_USD": 1.0,
        }

        for currency_code, wallet in self._wallets.items():
            if currency_code == base_currency:
                total_value += wallet.balance
            else:
                rate_key = f"{currency_code}_{base_currency}"
                if rate_key in demo_rates:
                    total_value += wallet.balance * demo_rates[rate_key]
                elif f"{base_currency}_{currency_code}" in demo_rates:
                    # Обратный курс
                    reverse_key = f"{base_currency}_{currency_code}"
                    total_value += wallet.balance / demo_rates[reverse_key]

        return total_value

    def to_dict(self) -> dict:
        """Преобразует объект в словарь"""
        return {
            "user_id": self._user_id,
            "wallets": {
                currency: wallet.to_dict() for currency, wallet in self._wallets.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        """Создает объект из словаря"""
        wallets = {}
        for currency, wallet_data in data.get("wallets", {}).items():
            wallets[currency] = Wallet.from_dict(wallet_data)
        return cls(user_id=data["user_id"], wallets=wallets)
