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
make run
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
- Python 3.8+
- Poetry (менеджер зависимостей)

## Структура проекта
```
finalproject_mishra_nod/
├── src/
│   └── finalproject_mishra_nod/
│       ├── __init__.py
│       └── __main__.py
├── tests/
├── docs/
├── pyproject.toml
├── Makefile
└── README.md
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
register --username <username> --password <password>

# Вход в систему
login --username <username> --password <password>

# Просмотр портфеля
show-portfolio [--base <currency>]

# Покупка валюты
buy --currency <code> --amount <amount>

# Продажа валюты
sell --currency <code> --amount <amount>

# Получение курса
get-rate --from <currency> --to <currency>
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
register --username alice --password 1234
login --username alice --password 1234
update-rates
buy --currency BTC --amount 0.01
buy --currency EUR --amount 100
show-portfolio
sell --currency BTC --amount 0.005
show-portfolio --base EUR
Запись сеанса работы
```

## Автор
mishra-alla email: [allasr22@gmail.com]