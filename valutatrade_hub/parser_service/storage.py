# valutatrade_hub/parser_service/storage.py
"""
Хранение исторических данных
"""

import json
import os
from datetime import datetime
from typing import Dict, List

from .config import ParserConfig


class RatesStorage:
    """Хранилище исторических данных курсов"""

    def __init__(self, config: ParserConfig):
        self.config = config
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Создает директорию для данных, если её нет"""
        data_dir = os.path.dirname(self.config.HISTORY_FILE_PATH)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def save_historical_record(
        self,
        from_currency: str,
        to_currency: str,
        rate: float,
        source: str,
        meta: Dict = None,
    ) -> str:
        """Сохраняет одну запись в историю"""
        # Генерируем ID как в задании: BTC_USD_2025-10-10T12:00:00Z
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        record_id = f"{from_currency}_{to_currency}_{timestamp}"
        record = {
            "id": record_id,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "rate": rate,
            "timestamp": timestamp,
            "source": source,
            "meta": meta or {},
        }
        # Загружаем существующие данные
        history = self.load_history()
        history.append(record)
        # Сохраняем обратно
        with open(self.config.HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, default=str)
        return record_id

    def load_history(self) -> List[Dict]:
        """Загружает исторические данные"""
        if not os.path.exists(self.config.HISTORY_FILE_PATH):
            return []
        try:
            with open(self.config.HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_current_rates(self, rates: Dict) -> None:
        """Сохраняет текущие курсы в rates.json"""
        current_data = {
            "pairs": rates,
            "last_refresh": datetime.now().isoformat(),
            "source": "ParserService",
        }
        with open(self.config.RATES_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2, default=str)

    def load_current_rates(self) -> Dict:
        """Загружает текущие курсы из rates.json"""
        if not os.path.exists(self.config.RATES_FILE_PATH):
            return {"pairs": {}, "last_refresh": None}
        try:
            with open(self.config.RATES_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"pairs": {}, "last_refresh": None}
