from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from api.database import (
    activate_user,
    activate_user_and_use_verification_code,
    close_db_pool,
    confirm_password_reset_transaction,
    create_user,
    create_user_rss_feed,
    delete_password_reset_token,
    delete_user,
    delete_user_rss_feed,
    get_active_verification_code,
    get_all_categories_list,
    get_all_category_ids,
    get_all_sources_list,
    get_db_pool,
    get_password_reset_token,
    get_recent_rss_items_for_broadcast,
    get_user_by_email,
    get_user_by_id,
    get_user_categories,
    get_user_rss_feed_by_id,
    get_user_rss_feeds,
    mark_verification_code_used,
    save_password_reset_token,
    save_verification_code,
    update_user,
    update_user_categories,
    update_user_password,
    update_user_rss_feed,
    verify_user_email,
)


@pytest.mark.asyncio
class TestDatabaseFunctions:
    @pytest.fixture
    def mock_pool(self):
        pool = AsyncMock()
        return pool

    @pytest.fixture
    def mock_conn(self):
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def mock_cur(self):
        cur = AsyncMock()
        return cur

    @pytest.fixture
    def async_cursor(self):
        """Создает курсор с поддержкой async iteration."""
        cur = MagicMock()

        class AsyncCursorIterator:
            def __init__(self, items):
                self.items = items
                self.index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.index < len(self.items):
                    item = self.items[self.index]
                    self.index += 1
                    return item
                raise StopAsyncIteration

        def set_results(items):
            cur.__aiter__ = lambda: AsyncCursorIterator(items)
            cur.execute = AsyncMock()

        cur.set_results = set_results
        return cur

    @pytest.fixture
    def mock_db_session(self, mock_pool, mock_conn, mock_cur):
        """Настраивает моки для асинхронного контекстного менеджера БД."""

        # Создаем простой класс для async context manager
        class AsyncContextManager:
            def __init__(self, return_value):
                self.return_value = return_value

            async def __aenter__(self):
                return self.return_value

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        # Настраиваем pool.acquire() как обычный метод (не AsyncMock)
        def acquire():
            return AsyncContextManager(mock_conn)

        mock_pool.acquire = acquire

        # Настраиваем conn.cursor() как обычный метод
        def cursor():
            return AsyncContextManager(mock_cur)

        mock_conn.cursor = cursor

        return mock_pool

    @pytest.fixture
    def async_db_session(self, mock_pool, mock_conn, async_cursor):
        """Настраивает моки для асинхронного контекстного менеджера БД с async cursor."""

        # Создаем простой класс для async context manager
        class AsyncContextManager:
            def __init__(self, return_value):
                self.return_value = return_value

            async def __aenter__(self):
                return self.return_value

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        # Настраиваем pool.acquire() как обычный метод (не AsyncMock)
        def acquire():
            return AsyncContextManager(mock_conn)

        mock_pool.acquire = acquire

        # Настраиваем conn.cursor() как обычный метод
        def cursor():
            return AsyncContextManager(async_cursor)

        mock_conn.cursor = cursor

        return mock_pool

    async def test_get_db_pool_success(self, mock_pool):
        with patch("config.get_shared_db_pool", return_value=mock_pool):
            result = await get_db_pool()
            assert result == mock_pool

    async def test_get_db_pool_failure(self):
        with patch("config.get_shared_db_pool", side_effect=Exception("DB error")):
            result = await get_db_pool()
            assert result is None

    async def test_close_db_pool_success(self):
        with patch("config.close_shared_db_pool", return_value=None):
            await close_db_pool()

    async def test_close_db_pool_failure(self):
        with patch("config.close_shared_db_pool", side_effect=Exception("DB error")):
            await close_db_pool()

    async def test_create_user_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            "test@example.com",
            "en",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("email",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await create_user(mock_db_session, "test@example.com", "hashed_pass", "en")
        assert result["email"] == "test@example.com"

    async def test_create_user_failure(self, mock_db_session, mock_cur):
        mock_cur.execute.side_effect = Exception("DB error")

        result = await create_user(mock_db_session, "test@example.com", "hashed_pass", "en")
        assert result is None

    async def test_get_user_by_email_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            "test@example.com",
            "hashed_pass",
            "en",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("email",),
            ("password_hash",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await get_user_by_email(mock_db_session, "test@example.com")
        assert result["email"] == "test@example.com"

    async def test_get_user_by_email_not_found(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = None

        result = await get_user_by_email(mock_db_session, "test@example.com")
        assert result is None

    async def test_get_user_by_id_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            "test@example.com",
            "hashed_pass",
            "en",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("email",),
            ("password_hash",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await get_user_by_id(mock_db_session, 1)
        assert result["id"] == 1

    async def test_update_user_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            "new@example.com",
            "hashed_pass",
            "es",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("email",),
            ("password_hash",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await update_user(
            mock_db_session, 1, {"email": "new@example.com", "language": "es"}
        )
        assert result["email"] == "new@example.com"

    async def test_update_user_no_changes(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            "test@example.com",
            "hashed_pass",
            "en",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("email",),
            ("password_hash",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await update_user(mock_db_session, 1, {})
        assert result["email"] == "test@example.com"

    async def test_delete_user_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await delete_user(mock_db_session, 1)
        assert result is True

    async def test_delete_user_not_found(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 0

        result = await delete_user(mock_db_session, 1)
        assert result is False

    async def test_activate_user_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await activate_user(mock_db_session, 1)
        assert result is True

    async def test_update_user_password_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await update_user_password(mock_db_session, 1, "new_hashed_pass")
        assert result is True

    async def test_save_verification_code_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await save_verification_code(
            mock_db_session, 1, "123456", datetime.now(UTC) + timedelta(hours=1)
        )
        assert result is True

    async def test_verify_user_email_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (1,)

        result = await verify_user_email(mock_db_session, "test@example.com", "123456")
        assert result == 1

    async def test_verify_user_email_not_found(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = None

        result = await verify_user_email(mock_db_session, "test@example.com", "123456")
        assert result is None

    async def test_get_active_verification_code_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            1,
            "123456",
            datetime.now(UTC),
            datetime.now(UTC) + timedelta(hours=1),
            None,
        )
        mock_cur.description = [
            ("id",),
            ("user_id",),
            ("verification_code",),
            ("created_at",),
            ("expires_at",),
            ("used_at",),
        ]

        result = await get_active_verification_code(mock_db_session, 1, "123456")
        assert result["verification_code"] == "123456"

    async def test_mark_verification_code_used_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await mark_verification_code_used(mock_db_session, 1)
        assert result is True

    async def test_save_password_reset_token_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await save_password_reset_token(
            mock_db_session, 1, "token123", datetime.now(UTC) + timedelta(hours=1)
        )
        assert result is True

    async def test_get_password_reset_token_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (1, datetime.now(UTC) + timedelta(hours=1))

        result = await get_password_reset_token(mock_db_session, "token123")
        assert result["user_id"] == 1

    async def test_get_password_reset_token_expired(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = None

        result = await get_password_reset_token(mock_db_session, "token123")
        assert result is None

    async def test_delete_password_reset_token_success(self, mock_db_session, mock_cur):
        result = await delete_password_reset_token(mock_db_session, "token123")
        assert result is True

    async def test_update_user_categories_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await update_user_categories(mock_db_session, 1, {1, 2, 3})
        assert result is True

    async def test_get_all_category_ids_success(self, mock_db_session, mock_cur):
        mock_cur.fetchall.return_value = [(1,), (2,), (3,)]

        result = await get_all_category_ids(mock_db_session)
        assert result == {1, 2, 3}

    @pytest.mark.skip(
        reason="Async mock iterator not working - TODO: fix with real DB or proper async mock"
    )
    async def test_get_user_categories_success(self, async_db_session, async_cursor):
        # Create async iterator class
        class AsyncIterator:
            def __init__(self):
                self.items = [(1, "Tech"), (2, "Sports")]
                self.index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.index < len(self.items):
                    item = self.items[self.index]
                    self.index += 1
                    return item
                raise StopAsyncIteration

        # Replace the mock with our async iterator
        async_cursor.__aiter__ = lambda: AsyncIterator()
        async_cursor.execute = AsyncMock()

        result = await get_user_categories(async_db_session, 1)
        assert len(result) == 2
        assert result[0]["name"] == "Tech"

    async def test_create_user_rss_feed_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            1,
            "http://example.com/rss",
            "Test Feed",
            1,
            "en",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("user_id",),
            ("url",),
            ("name",),
            ("category_id",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await create_user_rss_feed(
            mock_db_session, 1, "http://example.com/rss", "Test Feed", 1, "en"
        )
        assert result["name"] == "Test Feed"

    @pytest.mark.skip(
        reason="Async mock iterator not working - TODO: fix with real DB or proper async mock"
    )
    async def test_get_user_rss_feeds_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone = AsyncMock(
            side_effect=[
                (
                    1,
                    1,
                    "http://example.com/rss",
                    "Test Feed",
                    1,
                    "en",
                    True,
                    datetime.now(UTC),
                    datetime.now(UTC),
                ),
                None,
            ]
        )

        result = await get_user_rss_feeds(mock_db_session, 1, 10, 0)
        assert len(result) == 1
        assert result[0]["name"] == "Test Feed"

    async def test_get_user_rss_feed_by_id_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            1,
            "http://example.com/rss",
            "Test Feed",
            1,
            "en",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("user_id",),
            ("url",),
            ("name",),
            ("category_id",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await get_user_rss_feed_by_id(mock_db_session, 1, 1)
        assert result["id"] == 1

    async def test_update_user_rss_feed_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (
            1,
            1,
            "http://example.com/rss",
            "Updated Feed",
            1,
            "en",
            True,
            datetime.now(UTC),
            datetime.now(UTC),
        )
        mock_cur.description = [
            ("id",),
            ("user_id",),
            ("url",),
            ("name",),
            ("category_id",),
            ("language",),
            ("is_active",),
            ("created_at",),
            ("updated_at",),
        ]

        result = await update_user_rss_feed(mock_db_session, 1, 1, {"name": "Updated Feed"})
        assert result["name"] == "Updated Feed"

    async def test_delete_user_rss_feed_success(self, mock_db_session, mock_cur):
        mock_cur.rowcount = 1

        result = await delete_user_rss_feed(mock_db_session, 1, 1)
        assert result is True

    async def test_activate_user_and_use_verification_code_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (1,)

        result = await activate_user_and_use_verification_code(mock_db_session, 1, "123456")
        assert result is True

    async def test_confirm_password_reset_transaction_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone.return_value = (1, datetime.now(UTC) + timedelta(hours=1))
        mock_cur.rowcount = 1

        result = await confirm_password_reset_transaction(
            mock_db_session, "token123", "new_hashed_pass"
        )
        assert result is True

    @pytest.mark.skip(
        reason="Async mock iterator not working - TODO: fix with real DB or proper async mock"
    )
    async def test_get_all_categories_list_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone = AsyncMock(side_effect=[(2,), (1, "Tech"), (2, "Sports"), None])

        total_count, results = await get_all_categories_list(mock_db_session, 10, 0)
        assert total_count == 2
        assert len(results) == 2
        assert results[0]["name"] == "Tech"

    @pytest.mark.skip(
        reason="Async mock iterator not working - TODO: fix with real DB or proper async mock"
    )
    async def test_get_all_sources_list_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone = AsyncMock(
            side_effect=[(2,), (1, "BBC", "Description", "bbc", "logo.png", "http://bbc.com"), None]
        )

        total_count, results = await get_all_sources_list(mock_db_session, 10, 0)
        assert total_count == 2
        assert len(results) == 1
        assert results[0]["name"] == "BBC"

    @pytest.mark.skip(
        reason="Async mock iterator not working - TODO: fix with real DB or proper async mock"
    )
    async def test_get_recent_rss_items_for_broadcast_success(self, mock_db_session, mock_cur):
        mock_cur.fetchone = AsyncMock(
            side_effect=[
                (
                    "news1",
                    "Title",
                    "en",
                    "Tech",
                    datetime.now(UTC),
                    "Title RU",
                    "Content RU",
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
                None,
            ]
        )
        mock_cur.description = [
            ("news_id",),
            ("original_title",),
            ("original_language",),
            ("category_name",),
            ("published_at",),
            ("title_ru",),
            ("content_ru",),
            ("title_en",),
            ("content_en",),
            ("title_de",),
            ("content_de",),
            ("title_fr",),
            ("content_fr",),
        ]

        result = await get_recent_rss_items_for_broadcast(
            mock_db_session, datetime.now(UTC) - timedelta(hours=1)
        )
        assert len(result) == 1
        assert result[0]["news_id"] == "news1"
