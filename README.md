# Проект: Платформа для отслеживания и симуляции торговли валютами / Currency Trading Platform

## Описание проекта

### Цель проекта
Создать платформу ValutaTrade Hub, которая позволяет пользователям:

- Регистрироваться и управлять виртуальным портфелем валют
- Совершать сделки по покупке/продаже валют
- Отслеживать актуальные курсы в реальном времени
- Работать как с фиатными (USD, EUR, GBP, RUB, JPY), так и с криптовалютами (BTC, ETH, LTC, ADA)

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
│   ├── users.json          # JSON - пользователи
│   ├── portfolios.json     # JSON - портфели  
│   └── rates.json          # JSON - курсы
├── valutatrade_hub/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py       # User, Wallet, Portfolio
│   │   ├── utils.py        # DataManager, ExchangeRateService
│   │   └── usecases.py     # UserManager, PortfolioManager
│   └── cli/
│       ├── __init__.py
│       └── interface.py    # CLIInterface со всеми командами
├── main.py                 # Точка входа
├── Makefile                # Автоматизация
├── pyproject.toml          # Настройка Poetry
├── README.md               # Документация
├── .gitignore             # Игнорирование ненужных файлов
└── poetry.lock            # Фиксация версий
```

## Поддерживаемые валюты

### Фиатные валюты
USD (базовая), EUR, GBP, RUB, JPY

### Криптовалюты
BTC (Bitcoin), ETH (Ethereum), LTC (Litecoin), ADA (Cardano)

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
# Обновление всех курсов
update-rates
# Обновление только криптовалют
update-rates --source coingecko
# Обновление только фиатных валют  
update-rates --source exchangerate
# Просмотр кэшированных курсов
show-rates [--currency <code>] [--top <N>] [--base <currency>]
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
buy --currency EUR --amount 500
show-portfolio --base USD
Запись сеанса работы
```

## Автор
mishra-alla email: [allasr22@gmail.com]