"""
Декораторы для логирования
"""

import functools
import logging
from datetime import datetime
from typing import Callable, Any


def log_action(action: str, verbose: bool = False) -> Callable:
    """
    Декоратор для логирования действий

    Args:
        action: Название действия (BUY/SELL/REGISTER/LOGIN)
        verbose: Подробное логирование
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(__name__)

            try:
                # Получаем данные для логирования
                log_context = {
                    "action": action,
                    "timestamp": datetime.now().isoformat()[:19],  # Без микросекунд
                }

                # Получаем дополнительные параметры
                extra_params = {}
                if args and len(args) > 0:
                    # Для UserManager/PortfolioManager методов
                    if hasattr(args[0], "current_user") and args[0].current_user:
                        log_context["username"] = args[0].current_user.username
                    # Для buy/sell с user_id
                    elif len(args) >= 3 and isinstance(args[1], int):
                        log_context["user_id"] = args[1]

                # Выполняем функцию
                result = func(*args, **kwargs)

                # Формируем финальное сообщение в формате из задания
                if result and isinstance(result, dict):
                    log_message = f"{action} "

                    # Добавляем параметры
                    if "username" in log_context:
                        log_message += f"user='{log_context['username']}' "
                    elif "user_id" in log_context:
                        log_message += f"user_id={log_context['user_id']} "

                    # Добавляем данные из результата
                    if "currency" in result:
                        log_message += f"currency='{result['currency']}' "
                    if "amount" in result:
                        log_message += f"amount={result['amount']:.4f} "
                    if "rate" in result and result["rate"]:
                        log_message += f"rate={result['rate']:.2f} "
                    if "estimated_cost" in result and result["estimated_cost"]:
                        log_message += f"cost={result['estimated_cost']:.2f} "
                    elif "estimated_revenue" in result and result["estimated_revenue"]:
                        log_message += f"revenue={result['estimated_revenue']:.2f} "

                    log_message += "result=OK"

                    # Логируем в формате из задания
                    logger.info(log_message)

                return result

            except Exception as e:
                # Логируем ошибку
                error_message = f"{action} "
                if "username" in locals().get("log_context", {}):
                    error_message += f"user='{log_context['username']}' "
                error_message += f"result=ERROR error='{type(e).__name__}: {str(e)}'"

                logger.error(error_message)

                # Пробрасываем исключение дальше
                raise

        return wrapper

    return decorator
