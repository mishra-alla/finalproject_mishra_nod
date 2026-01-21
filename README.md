# Проект: Платформа для отслеживания и симуляции торговли валютами / Currency Trading Platform

## Описание проекта

### Цель проекта
Создать платформу ValutaTrade Hub, которая позволяет пользователям:

- Регистрироваться и управлять виртуальным портфелем валют
- Совершать сделки по покупке/продаже валют
- Отслеживать актуальные курсы в реальном времени
- Работать как с фиатными (USD, EUR, RUB), так и с криптовалютами (BTC, ETH)

### Результат:
Полноценное консольное приложение, имитирующее работу валютного кошелька, которое можно установить и запустить как самостоятельный пакет (полноценный Python-пакет).

## Установка
```
# Клонирование репозитория
git clone <your-repo-url>
cd project2_Mishra_Alla

# Установка зависимостей
poetry install      # через poetry
make install        # через Makefile

# Запуск
poetry run project  # через poetry
make project        # через Makefile
make run            # то же самое что make project
```
### Дополнительные команды Makefile

- `make build` - сборка пакета
- `make package-install` - установка собранного пакета через pip
- `make lint` - проверка кода
- `make format` - форматирование кода
- `make test` - запуск тестов
- `make clean` - очистка временных файлов
- `make publish` - Публикация пакета в репозиторий (если настроено)

### Предварительные требования
- Python 3.12+
- Poetry (менеджер зависимостей)

## Структура проекта
```
finalproject_mishra_nod/
├── data/
│   ├── users.json              # JSON - пользователи
│   ├── portfolios.json         # JSON - портфели
│   ├── rates.json              # Текущие курсы
│   └── exchange_rates.json     # Исторические данные
├── valutatrade_hub/
│   ├── parser_service/         # Парсер валют
│   │   ├── __init__.py
│   │   ├── config.py           # Конфигурация с Dataclass, ParserConfig
│   │   ├── api_clients.py      # BaseApiClient + наследники
│   │   ├── storage.py          # Хранение исторических данных
│   │   ├── updater.py          # RatesUpdater
│   │   └── scheduler.py        #  Планировщик
│   ├── core/
│   │   ├── currencies.py       # Иерархия валют
│   │   ├── exceptions.py       # Пользовательские исключения
│   │   ├── models.py           # User, Wallet, Portfolio
│   │   ├── usecases.py         # Бизнес-логика с декораторами
│   │   └── utils.py            # Вспомогательные функции
│   ├── infra/
│   │   ├── settings.py         # Singleton SettingsLoader
│   │   └── database.py         # Singleton DatabaseManager
│   ├── cli/
│   │   └── interface.py        # CLI с новыми командами
│   ├── logging_config.py       # Настройка логов
│   └── decorators.py           # @log_action
├── main.py                     # Точка входа
├── Makefile                    # Автоматизация
├── pyproject.toml              # Настройка Poetry
├── README.md                   # Документация
├── .gitignore                  # Игнорирование ненужных файлов
└── data/                       # НЕ в коммите (.gitignore)
    ├── *.json                  # Генерируются при работе
```

## Поддерживаемые валюты

### Фиатные валюты
USD (базовая), EUR, RUB

### Криптовалюты
BTC (Bitcoin), ETH (Ethereum)

## Команды

### Основные операции
```bash
# Регистрация
register --username <имя> --password <пароль>
# Вход в систему
login --username <имя> --password <пароль>
# Просмотр портфеля
show-portfolio [--base <валюта>]
# Покупка валюты
buy --currency <код> --amount <сумма>
# Продажа валюты
sell --currency <код> --amount <сумма>
# Получение курса
get-rate --from <валюта> --to <валюта>
# Просмотр информации кошелька пользователя
show-portfolio [--base <валюта>]
```

### Работа с курсами
```bash
# курсы  одной валюты отгносительно другой
get-rate --from <валюта> --to <валюта>
# Обновление курсов валют [крипто/фиатной]
update-rates [--source <coingecko|exchangerate>]
# Просмотр кэшированных курсов
show-rates [--currency <код>] [--top <N>] [--base <валюта>]
# Список поддерживаемых валют
list-currencies
```

### Примеры использования
```bash
# Полный цикл работы
register --username Иван --password 7890
buy --currency BTC --amount 0.05
get-rate --from USD --to BTC
show-portfolio
buy --currency USD --amount 200
update-rates --source exchangerate
update-rates
show-rates --top 10
buy --currency RUB --amount 500
show-portfolio --base USD
```

## Автор
mishra-alla email: [allasr22@gmail.com]