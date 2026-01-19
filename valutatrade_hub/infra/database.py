"""
Singleton для управления базой данных (JSON)
"""

import json
import os
from typing import Any
from threading import Lock
# from .settings import DATA_DIR  # Импортируем константу


class DatabaseManager:
    """Singleton для работы с JSON базой данных"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if not self._initialized:
            self.data_dir = "data"  # Прямо прописываем
            self._ensure_data_dir()
            self._initialized = True

    def _ensure_data_dir(self) -> None:
        """Создает директорию для данных, если её нет"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_file_path(self, filename: str) -> str:
        """Возвращает полный путь к файлу"""
        return os.path.join(self.data_dir, filename)

    def load(self, filename: str, default: Any = None) -> Any:
        """Загружает данные из JSON файла"""
        filepath = self._get_file_path(filename)
        if not os.path.exists(filepath):
            return default if default is not None else []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default if default is not None else []

    def save(self, filename: str, data: Any) -> None:
        """Сохраняет данные в JSON файл"""
        filepath = self._get_file_path(filename)

        with self._lock:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def update(
        self, filename: str, key: str, value: Any, id_field: str = "user_id"
    ) -> bool:
        """Обновляет запись в файле по ключу"""
        data = self.load(filename, [])

        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict) and item.get(id_field) == key:
                    if isinstance(value, dict):
                        data[i].update(value)
                    else:
                        data[i] = value
                    self.save(filename, data)
                    return True

        return False

    def get_next_user_id(self) -> int:
        """Генерирует следующий ID пользователя"""
        users = self.load("users.json", [])
        if not users:
            return 1
        return max(user.get("user_id", 0) for user in users) + 1
