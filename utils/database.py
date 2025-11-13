import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, Concatenate, ParamSpec, TypeVar

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


def db_operation(
    func: Callable[Concatenate[Any, Any, P], Awaitable[R]],
) -> Callable[Concatenate[Any, P], Awaitable[R | None]]:
    """
    Декоратор для операций с базой данных.
    Автоматически получает пул, обрабатывает ошибки и логирует.

    Декорируемая функция должна принимать:
    - self (экземпляр класса) - Any
    - pool (пул подключений БД) - добавляется автоматически декоратором
    - *args, **kwargs (остальные параметры) - P

    Возвращает:
    - R | None: результат оригинальной функции или None при ошибке

    Пример использования:
        class MyManager(DatabaseMixin):
            @db_operation
            async def get_data(self, pool, user_id: int) -> dict:
                async with pool.acquire() as conn, conn.cursor() as cur:
                    await cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                    return await cur.fetchone()
    """

    @wraps(func)
    async def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> R | None:
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
