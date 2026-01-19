"""
Singleton для загрузки настроек
"""


class SettingsLoader:
    """Singleton для загрузки настроек"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = {
                "data_dir": "data",
                "default_base_currency": "USD",
                "rates_ttl_seconds": 300,
                "log_file": "valutatrade.log",
            }
        return cls._instance

    def get(self, key: str, default=None):
        """Возвращает значение настройки."""
        return self._settings.get(key, default)
