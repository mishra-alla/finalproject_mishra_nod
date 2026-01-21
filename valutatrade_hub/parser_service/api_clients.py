# valutatrade_hub/parser_service/api_clients.py
"""
Клиенты для работы с внешними API
"""

import time
import json
from typing import Dict
import requests
from abc import ABC, abstractmethod

from .config import ParserConfig


class BaseApiClient(ABC):
    """Базовый класс API клиента"""

    def __init__(self, config: ParserConfig):
        self.config = config

    @abstractmethod
    def fetch_rates(self) -> dict:
        """Получаем курсы валют с метаданными"""
        pass


class CoinGeckoClient(BaseApiClient):
    """Клиент для CoinGecko API"""

    def fetch_rates(self) -> Dict:
        """Получает курсы криптовалют от CoinGecko."""
        try:
            url = self.config.COINGECKO_URL
            params = {
                "ids": ",".join(self.config.CRYPTO_ID_MAP.values()),
                "vs_currencies": "usd",
            }

            response = requests.get(
                url, params=params, timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            rates = {}
            for code, api_id in self.config.CRYPTO_ID_MAP.items():
                if api_id in data and "usd" in data[api_id]:
                    rate_key = f"{code}_{self.config.BASE_CURRENCY}"
                    rates[rate_key] = {
                        "rate": data[api_id]["usd"],
                        "source": "CoinGecko",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }

            return rates

        except Exception:
            # Если API не работает, возвращаем пустой словарь
            return {}


class ExchangeRateApiClient(BaseApiClient):
    """Клиент для ExchangeRate-API"""

    def fetch_rates(self) -> Dict:
        """Получает курсы фиатных валют от ExchangeRate-API"""
        try:
            url = self.config.EXCHANGERATE_API_URL

            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                return {}

            rates = {}
            # Проверяем разные форматы ответа ExchangeRate-API
            if "conversion_rates" in data:
                all_rates = data.get("conversion_rates", {})
                base_currency = data.get("base_code", "USD")
                # print(f"Доступно валют: {len(all_rates)}")

            elif "rates" in data:
                all_rates = data.get("rates", {})
                base_currency = data.get("base_code", "USD")
                # print(f"Доступно валют: {len(all_rates)}")

            else:
                # print(f"Пример данных: {str(data)[:200]}...")
                return {}

            # Берем валюты из конфига
            found_count = 0
            for currency in self.config.FIAT_CURRENCIES:
                if currency in all_rates:
                    rate_key = f"{currency}_{base_currency}"
                    rates[rate_key] = {
                        "rate": float(all_rates[currency]),
                        "source": "ExchangeRate-API",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "meta": {
                            "base_currency": base_currency,
                            "time_last_update": data.get("time_last_update_utc", ""),
                        },
                    }
                    found_count += 1
                else:
                    print(f"  Валюта {currency} не найдена в ответе API")

            # Всегда добавляем базовую валюту
            base_key = f"{base_currency}_{base_currency}"
            rates[base_key] = {
                "rate": 1.0,
                "source": "ExchangeRate-API",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "meta": {
                    "base_currency": base_currency,
                    "time_last_update": data.get("time_last_update_utc", ""),
                },
            }
            found_count += 1

            print(f"Всего получено {len(rates)} фиатных курсов")
            return rates

        except requests.exceptions.RequestException as e:
            print(f"Ошибка соединения с ExchangeRate-API: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON от ExchangeRate-API: {e}")
            return {}
        except Exception as e:
            print(f"Неожиданная ошибка ExchangeRate-API: {e}")
            return {}
