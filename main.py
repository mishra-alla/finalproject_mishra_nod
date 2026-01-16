#!/usr/bin/env python3
"""
Главный файл запуска приложения.
"""

from valutatrade_hub.cli.interface import CLIInterface


def main() -> None:
    """Основная точка входа в приложение"""
    print("VALUTATRADE HUB - Платформа для торговли валютами")
    print("-" * 60)

    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()
