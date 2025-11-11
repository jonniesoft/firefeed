import logging
from typing import Callable, TypeVar, ParamSpec, Awaitable
from functools import wraps
from config import get_shared_db_pool

logger = logging.getLogger(__name__)


# Типы для точной аннотации async-декоратора
P = ParamSpec("P")
R = TypeVar("R")


class DatabaseMixin:
    """Базовый класс для работы с базой данных"""

    async def get_pool(self):
        """Получает общий пул подключений из config.py"""
        return await get_shared_db_pool()

    async def close_pool(self):
        """Заглушка - пул закрывается глобально"""
        pass


def db_operation(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """
    Декоратор для операций с базой данных.
    Автоматически получает пул, обрабатывает ошибки и логирует.
    """

    @wraps(func)
    async def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
        try:
            pool = await self.get_pool()
            if pool is None:
                logger.error("[DB] Не удалось получить пул подключений")
                return None

            # Вызываем оригинальную функцию с пулом
            return await func(self, pool, *args, **kwargs)

        except Exception as e:
            logger.error(f"[DB] Ошибка в {func.__name__}: {e}")
            return None

    return wrapper
