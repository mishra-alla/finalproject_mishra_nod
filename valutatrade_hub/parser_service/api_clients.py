# valutatrade_hub/parser_service/api_clients.py
"""
Клиенты для работы с внешними API
"""

import time
from typing import Dict
import requests
from abc import ABC, abstractmethod


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> dict:
        pass


class CoinGeckoClient(BaseApiClient):
    def fetch_coingecko_rates() -> Dict:
        """Получает курсы криптовалют от CoinGecko."""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            rates = {}
            crypto_map = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}

            for api_id, code in crypto_map.items():
                if api_id in data and "usd" in data[api_id]:
                    rate_key = f"{code}_USD"
                    rates[rate_key] = {
                        "rate": data[api_id]["usd"],
                        "source": "CoinGecko",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }

            return rates

        except Exception:
            # Если API не работает, возвращаем пустой словарь
            return {}

    def fetch_exchangerate_rates() -> Dict:
        """Получает курсы фиатных валют от ExchangeRate-API."""
        try:
            url = (
                "https://v6.exchangerate-api.com/v6/a4be4deebef7c25150f142c8/latest/USD"
            )

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                return {}

            rates = {}
            fiat_currencies = ["EUR", "GBP", "RUB", "CNY"]

            for currency in fiat_currencies:
                if currency in data.get("rates", {}):
                    rate_key = f"{currency}_USD"
                    rates[rate_key] = {
                        "rate": data["rates"][currency],
                        "source": "ExchangeRate-API",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }

            # Добавляем USD
            rates["USD_USD"] = {
                "rate": 1.0,
                "source": "ExchangeRate-API",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            return rates

        except Exception:
            # Если API не работает, возвращаем пустой словарь
            return {}
