# valutatrade_hub/parser_service/updater.py

"""
Простой обновлятель курсов
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from .config import ParserConfig
from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .storage import RatesStorage


class RatesUpdater:
    """Координатор обновления курсов"""

    def __init__(self):
        self.config = ParserConfig()
        self.storage = RatesStorage(self.config)
        self.logger = logging.getLogger(__name__)

        # Инициализируем клиенты
        self.coingecko_client = CoinGeckoClient(self.config)
        self.exchangerate_client = ExchangeRateApiClient(self.config)

    def run_update(self, source: Optional[str] = None) -> Dict:
        """Запускает обновление курсов"""
        # Логируем правильный источник
        if source:
            self.logger.info(f"Starting rates update (source: {source})")
        else:
            self.logger.info("Starting rates update (source: all)")

        all_rates = {}

        try:
            # 1. Получаем курсы криптовалют
            should_fetch_crypto = source in (None, "coingecko")
            should_fetch_fiat = source in (None, "exchangerate")

            if should_fetch_crypto:
                self.logger.info("Fetching crypto rates from CoinGecko...")
                crypto_rates = self.coingecko_client.fetch_rates()
                if crypto_rates:
                    all_rates.update(crypto_rates)
                    self.logger.info(f"Got {len(crypto_rates)} crypto rates")
                else:
                    self.logger.warning("No crypto rates received from CoinGecko")

            if should_fetch_fiat:
                self.logger.info("Fetching fiat rates from ExchangeRate-API...")
                fiat_rates = self.exchangerate_client.fetch_rates()
                if fiat_rates:
                    all_rates.update(fiat_rates)
                    self.logger.info(f"Got {len(fiat_rates)} fiat rates")
                else:
                    self.logger.warning("No fiat rates received from ExchangeRate-API")

            # 2. Если API не вернули данные, используем демо
            if not all_rates:
                self.logger.warning("API returned no data, using demo")
                all_rates = self._get_demo_rates()

            # 3. Сохраняем текущие курсы
            if all_rates:
                self.storage.save_current_rates(all_rates)

                # 4. Сохраняем в историю
                for rate_key, rate_data in all_rates.items():
                    from_currency, to_currency = rate_key.split("_")
                    self.storage.save_historical_record(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=rate_data["rate"],
                        source=rate_data["source"],
                        meta=rate_data.get("meta", {}),
                    )
                self.logger.info(f"Update complete. Total rates: {len(all_rates)}")
                return all_rates
            else:
                self.logger.error("Failed to get any rates")
                return {}
        except Exception as e:
            self.logger.error(f"Critical update error: {e}")
            return self._get_demo_rates()

    def _get_demo_rates(self) -> Dict:
        """Возвращает демонстрационные курсы"""
        demo_rates = {
            "BTC_USD": {
                "rate": 59337.21,
                "source": "Demo",
                "timestamp": datetime.now().isoformat(),
                "meta": {"note": "demo_data"},
            },
            "ETH_USD": {
                "rate": 3720.00,
                "source": "Demo",
                "timestamp": datetime.now().isoformat(),
                "meta": {"note": "demo_data"},
            },
            "EUR_USD": {
                "rate": 1.0786,
                "source": "Demo",
                "timestamp": datetime.now().isoformat(),
                "meta": {"note": "demo_data"},
            },
            "USD_USD": {
                "rate": 1.0,
                "source": "Demo",
                "timestamp": datetime.now().isoformat(),
                "meta": {"note": "demo_data"},
            },
        }

        # Сохраняем демо-данные
        self.storage.save_current_rates(demo_rates)

        return demo_rates
