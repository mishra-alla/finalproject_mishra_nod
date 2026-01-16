"""
Вспомогательные функции и классы
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict


class DataManager:
    """Менеджер данных для работы с JSON файлами."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Создает папку для данных, если она не существует."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_file_path(self, filename: str) -> str:
        """Возвращает полный путь к файлу."""
        return os.path.join(self.data_dir, filename)

    def load_json(self, filename: str, default: Any = None) -> Any:
        """Читает JSON файл и возвращает данные."""
        filepath = self._get_file_path(filename)
        if not os.path.exists(filepath):
            return default if default is not None else []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default if default is not None else []

    def save_json(self, filename: str, data: Any):
        """Записывает данные в JSON файл."""
        filepath = self._get_file_path(filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def get_next_user_id(self) -> int:
        """Генерирует следующий ID пользователя."""
        users = self.load_json("users.json", [])
        if not users:
            return 1
        return max(user["user_id"] for user in users) + 1


class ExchangeRateService:
    """Сервис для работы с курсами валют."""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def get_rates(self) -> Dict:
        """Загружает котировки из rates.json."""
        rates = self.data_manager.load_json("rates.json", {})
        if not rates:
            return {"pairs": {}, "last_refresh": None}
        return rates

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """Получает обменный курс."""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return 1.0

        rates = self.get_rates()

        # Прямой курс
        rate_key = f"{from_currency}_{to_currency}"
        if rate_key in rates.get("pairs", {}):
            return rates["pairs"][rate_key]["rate"]

        # Обратный курс
        reverse_key = f"{to_currency}_{from_currency}"
        if reverse_key in rates.get("pairs", {}):
            return 1.0 / rates["pairs"][reverse_key]["rate"]

        # Если курс не найден, используем демо-курсы
        demo_rates = {
            "BTC_USD": 59337.21,
            "EUR_USD": 1.0786,
            "RUB_USD": 0.01016,
            "ETH_USD": 3720.00,
        }

        if rate_key in demo_rates:
            return demo_rates[rate_key]
        elif reverse_key in demo_rates:
            return 1.0 / demo_rates[reverse_key]

        return None

    def is_rates_fresh(self, ttl_seconds: int = 300) -> bool:
        """Проверяет актуальность курсов"""
        rates = self.get_rates()
        if "last_refresh" not in rates or not rates["last_refresh"]:
            return False

        try:
            last_refresh = datetime.fromisoformat(rates["last_refresh"])
            return (datetime.now() - last_refresh) < timedelta(seconds=ttl_seconds)
        except (ValueError, KeyError):
            return False

    def update_rates(self, new_rates: Dict):
        """Обновляет курсы валют"""
        current_rates = self.get_rates()
        current_rates.update(new_rates)
        current_rates["last_refresh"] = datetime.now().isoformat()
        self.data_manager.save_json("rates.json", current_rates)


# def validate_currency_code(currency_code: str) -> bool:
#    """Проверяет валидность кода валюты"""
#    return (isinstance(currency_code, str) and
#            len(currency_code) >= 2 and
#            len(currency_code) <= 5 and
#            currency_code.isalpha())


# def validate_amount(amount: float) -> bool:
#    """Проверяет валидность суммы"""
#    return isinstance(amount, (int, float)) and amount > 0
