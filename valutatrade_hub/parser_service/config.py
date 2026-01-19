# valutatrade_hub/parser_service/config.py
from dataclasses import dataclass


@dataclass
class ParserConfig:
    """Конфигурация для сервиса парсинга"""

    # API ключ (ваш)
    EXCHANGERATE_API_KEY = "a4be4deebef7c25150f142c8"

    # URL API
    COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL = (
        f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD"
    )

    # Валюты для отслеживания
    FIAT_CURRENCIES = ["EUR", "GBP", "RUB", "CNY"]
    CRYPTO_CURRENCIES = ["BTC", "ETH", "SOL"]

    # Соответствие крипто-кодов
    CRYPTO_ID_MAP = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}

    # Файлы
    RATES_FILE = "data/rates.json"
    HISTORY_FILE = "data/exchange_rates.json"
