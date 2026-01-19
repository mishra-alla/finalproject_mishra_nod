"""
Простой обновлятель курсов.
"""

import json
from datetime import datetime
from typing import Optional, Dict
import requests


def update_rates(source: Optional[str] = None) -> Dict:
    """
    Обновляет курсы валют

    Args:
        source: 'coingecko', 'exchangerate', или None для всех

    Returns:
        Словарь с курсами
    """
    all_rates = {}

    # 1. Пытаемся получить реальные курсы
    if source in (None, "coingecko"):
        crypto_rates = fetch_coingecko_rates()
        if crypto_rates:
            all_rates.update(crypto_rates)
            print(" Получены курсы криптовалют")

    if source in (None, "exchangerate"):
        fiat_rates = fetch_exchangerate_rates()
        if fiat_rates:
            all_rates.update(fiat_rates)
            print(" Получены курсы фиатных валют")

    # 2. Если не получили реальных данных, используем демо
    if not all_rates:
        print("!!! API недоступны, использую демо-данные")
        all_rates = get_demo_rates()

    # 3. Сохраняем в rates.json
    save_rates(all_rates)

    # 4. Сохраняем в историю
    save_to_history(all_rates)

    return all_rates


def fetch_coingecko_rates() -> Dict:
    """Получает курсы криптовалют от CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        rates = {}
        crypto_map = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}

        for api_id, code in crypto_map.items():
            if api_id in data and "usd" in data[api_id]:
                rate_key = f"{code}_USD"
                rates[rate_key] = {
                    "rate": data[api_id]["usd"],
                    "source": "CoinGecko",
                    "timestamp": datetime.now().isoformat(),
                }

        return rates

    except Exception as e:
        print(f"!!! CoinGecko error: {e}")
        return {}


def fetch_exchangerate_rates() -> Dict:
    """Получает курсы фиатных валют от ExchangeRate-API"""
    try:
        url = "https://v6.exchangerate-api.com/v6/a4be4deebef7c25150f142c8/latest/USD"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            print(f"!!! ExchangeRate API error: {data.get('error-type', 'unknown')}")
            return {}

        rates = {}
        fiat_currencies = ["EUR", "GBP", "RUB", "CNY", "JPY"]

        for currency in fiat_currencies:
            if currency in data.get("rates", {}):
                rate_key = f"{currency}_USD"
                rates[rate_key] = {
                    "rate": data["rates"][currency],
                    "source": "ExchangeRate-API",
                    "timestamp": datetime.now().isoformat(),
                }

        # Добавляем USD
        rates["USD_USD"] = {
            "rate": 1.0,
            "source": "ExchangeRate-API",
            "timestamp": datetime.now().isoformat(),
        }

        return rates

    except Exception as e:
        print(f"!!! ExchangeRate-API error: {e}")
        return {}


def get_demo_rates() -> Dict:
    """Демонстрационные курсы"""
    return {
        "BTC_USD": {
            "rate": 59337.21,
            "source": "Demo",
            "timestamp": datetime.now().isoformat(),
        },
        "ETH_USD": {
            "rate": 3720.00,
            "source": "Demo",
            "timestamp": datetime.now().isoformat(),
        },
        "EUR_USD": {
            "rate": 1.0786,
            "source": "Demo",
            "timestamp": datetime.now().isoformat(),
        },
        "RUB_USD": {
            "rate": 0.01016,
            "source": "Demo",
            "timestamp": datetime.now().isoformat(),
        },
        "USD_USD": {
            "rate": 1.0,
            "source": "Demo",
            "timestamp": datetime.now().isoformat(),
        },
    }


def save_rates(rates: Dict) -> None:
    """Сохраняет курсы в rates.json"""
    data = {
        "pairs": rates,
        "last_refresh": datetime.now().isoformat(),
        "source": "ParserService",
    }

    with open("data/rates.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_to_history(rates: Dict) -> None:
    """Сохраняет курсы в историю"""
    try:
        # Загружаем существующую историю
        with open("data/exchange_rates.json", "r", encoding="utf-8") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    # Добавляем новые записи
    for pair, data in rates.items():
        from_curr, to_curr = pair.split("_")
        history.append(
            {
                "pair": pair,
                "from": from_curr,
                "to": to_curr,
                "rate": data["rate"],
                "source": data["source"],
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
            }
        )

    # Сохраняем обратно
    with open("data/exchange_rates.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, default=str)


def load_current_rates() -> Dict:
    """Загружает текущие курсы"""
    try:
        with open("data/rates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pairs": {}, "last_refresh": None}
