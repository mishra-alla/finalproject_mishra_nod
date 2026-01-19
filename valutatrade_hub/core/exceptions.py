"""
Пользовательские исключения
"""


class ValutaTradeError(Exception):
    """Базовое исключение для всех ошибок системы"""

    pass


class InsufficientFundsError(ValutaTradeError):
    """Недостаточно средств на счете"""

    def __init__(self, currency_code: str, available: float, required: float):
        self.currency_code = currency_code
        self.available = available
        self.required = required
        super().__init__(
            f"Недостаточно средств: доступно {available:.4f} {currency_code}, "
            f"требуется {required:.4f} {currency_code}"
        )


class CurrencyNotFoundError(ValutaTradeError):
    """Неизвестная валюта"""

    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        super().__init__(f"Неизвестная валюта '{currency_code}'")


class ApiRequestError(ValutaTradeError):
    """Ошибка при обращении к внешнему API"""

    def __init__(self, reason: str = "Неизвестная ошибка"):
        self.reason = reason
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")


class ValidationError(ValutaTradeError):
    """Ошибка валидации данных"""

    pass
