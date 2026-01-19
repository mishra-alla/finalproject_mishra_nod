#!/usr/bin/env python3
"""
Главный файл запуска приложения
"""

import sys

from valutatrade_hub.cli.interface import CLIInterface
from valutatrade_hub.logging_config import setup_logging


def main() -> None:
    """Основная точка входа в приложение."""
    try:
        # Настраиваем логирование
        setup_logging()

        print("=" * 60)
        print("VALUTATRADE HUB - Платформа для торговли валютами")
        print("=" * 60)

        cli = CLIInterface()
        cli.run()

    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
