# valutatrade_hub/parser_service/config.py
"""
Конфигурация для сервиса парсинга
"""

import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ParserConfig:
    """Конфигурация парсера курсов"""

    # API ключ ExchangeRate-API
    # EXCHANGERATE_API_KEY: str = "a4be4deebef7c25150f142c8"
    EXCHANGERATE_API_KEY: str = os.getenv(
        "EXCHANGE_RATE_API_KEY", "a4be4deebef7c25150f142c8"
    )

    # URL API
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = (
        f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD"
    )
    # EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"
    # EXCHANGERATE_API_URL: str = "https://api.exchangerate-api.com/v4/latest"
    # EXCHANGERATE_API_URL: str = "https://api.exchangerate-api.com/v4"
    # EXCHANGERATE_API_URL: str = "https://open.er-api.com/v6/latest"

    # Базовая валюта
    BASE_CURRENCY: str = "USD"

    # Списки валют для отслеживания
    FIAT_CURRENCIES = ("EUR", "GBP", "RUB", "CNY", "JPY")
    CRYPTO_CURRENCIES = ("BTC", "ETH", "SOL")

    # Соответствие кодов криптовалют - используем field с default_factory
    CRYPTO_ID_MAP: Dict[str, str] = field(
        default_factory=lambda: {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
    )
    # Пути к файлам
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    # Параметры запросов
    REQUEST_TIMEOUT: int = 30

    def get_exchangerate_url(self) -> str:
        """Возвращает URL для ExchangeRate-API"""
        return f"{self.EXCHANGERATE_API_URL}/{self.EXCHANGERATE_API_KEY}\
                                                /latest/{self.BASE_CURRENCY}"
