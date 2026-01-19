"""
Иерархия валют
"""

from abc import ABC, abstractmethod
from typing import Dict

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    """базовый класс валюты"""

    def __init__(self, name: str, code: str):
        if not name or not name.strip():
            raise ValueError("Название валюты не может быть пустым")
        if not code or not code.strip():
            raise ValueError("Код валюты не может быть пустым")

        code = code.upper().strip()
        if not (2 <= len(code) <= 5 and code.isalpha()):
            raise ValueError(f"Некорректный код валюты: {code}")

        self.name = name
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        """Строковое представление для UI/логов"""
        pass

    def __str__(self) -> str:
        return self.get_display_info()


class FiatCurrency(Currency):
    """Фиатная валюта"""

    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    """Криптовалюта"""

    def __init__(self, name: str, code: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        mcap = (
            f"{self.market_cap:.2e}"
            if self.market_cap > 1000
            else f"{self.market_cap:.2f}"
        )
        return (
            f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {mcap})"
        )


# Реестр валют
_CURRENCIES: Dict[str, Currency] = {}


def register_currency(currency: Currency) -> None:
    """Регистрирует валюту в реестре"""
    _CURRENCIES[currency.code] = currency


def get_currency(code: str) -> Currency:
    """Возвращает валюту по коду"""
    code = code.upper()
    if code not in _CURRENCIES:
        raise CurrencyNotFoundError(code)
    return _CURRENCIES[code]


def get_all_currencies() -> Dict[str, Currency]:
    """Возвращает все зарегистрированные валюты"""
    return _CURRENCIES.copy()


# Инициализация демо-валют
register_currency(FiatCurrency("US Dollar", "USD", "United States"))
register_currency(FiatCurrency("Euro", "EUR", "Eurozone"))
register_currency(FiatCurrency("Russian Ruble", "RUB", "Russia"))
register_currency(CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12))
register_currency(CryptoCurrency("Ethereum", "ETH", "Ethash", 3.72e11))
