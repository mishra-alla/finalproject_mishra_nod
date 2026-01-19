"""
Настройка логов.
"""

import logging


def setup_logging() -> None:
    """Настраивает логирование."""
    # Простое консольное логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Логирование настроено")
