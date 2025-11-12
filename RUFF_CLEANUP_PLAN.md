# План устранения оставшихся 92 ошибок Ruff

**Дата создания:** 2025-11-12
**Текущий статус:** 92 ошибки после завершения PTH миграции
**Цель:** Систематическое устранение всех нетривиальных ошибок качества кода

---

## Приоритизация ошибок

### 🔴 **Приоритет 1: Критические (потенциальные баги и нарушения стандартов)**

#### **Фаза 1.1: RUF013 - Implicit Optional (5 ошибок)** ⚠️ Нарушение PEP 484
**Приоритет:** Высокий
**Сложность:** Низкая
**Время:** ~10 мин
**Риск:** Минимальный

**Локации:**
- `bot.py:69` - `mark_translation_as_published(message_id: int = None)`
- `bot.py:93` - `mark_original_as_published(message_id: int = None)`
- `bot.py:135` - `api_get(params: dict = None)`
- `bot.py:172` - `get_rss_items_list(display_language: str = None)`
- `firefeed_dublicate_detector.py:140` - `get_similar_rss_items(current_rss_item_id: str = None)`

**Исправление:**
```python
# До:
async def mark_translation_as_published(translation_id: int, channel_id: int, message_id: int = None):

# После:
async def mark_translation_as_published(translation_id: int, channel_id: int, message_id: int | None = None):
```

**Тестирование:**
- Проверка через `uv run --no-project ruff check . --select RUF013`
- Запуск бота для проверки корректности работы функций

---

#### **Фаза 1.2: RUF012 - Mutable Class Defaults (3 ошибки)** ⚠️ Потенциальные баги
**Приоритет:** Высокий
**Сложность:** Низкая
**Время:** ~5 мин
**Риск:** Минимальный

**Локации:**
- `firefeed_embeddings_processor.py:17-19` - класс `FireFeedEmbeddingsProcessor`
  - `_model_cache = {}`
  - `_spacy_cache = {}`
  - `_spacy_usage_order = []`

**Исправление:**
```python
# До:
class FireFeedEmbeddingsProcessor:
    _instance = None
    _model_cache = {}
    _spacy_cache = {}
    _spacy_usage_order = []

# После:
from typing import ClassVar

class FireFeedEmbeddingsProcessor:
    _instance: ClassVar[FireFeedEmbeddingsProcessor | None] = None
    _model_cache: ClassVar[dict[str, Any]] = {}
    _spacy_cache: ClassVar[dict[str, Any]] = {}
    _spacy_usage_order: ClassVar[list[str]] = []
```

**Тестирование:**
- Проверка через `uv run --no-project ruff check . --select RUF012`
- Запуск embeddings процессора для проверки синглтона

---

#### **Фаза 1.3: RUF006 - Asyncio Dangling Task (2 ошибки)** ⚠️ Утечки памяти
**Приоритет:** Высокий
**Сложность:** Средняя
**Время:** ~10 мин
**Риск:** Низкий

**Локации:**
- `api/app.py:29` - `asyncio.create_task(check_for_new_rss_items())`

**Исправление:**
```python
# До:
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    asyncio.create_task(check_for_new_rss_items())
    logger.info("[Startup] RSS items checking task started")

# После:
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    rss_task = asyncio.create_task(check_for_new_rss_items())
    logger.info("[Startup] RSS items checking task started")

    try:
        yield
    finally:
        # Cleanup: cancel task if still running
        if not rss_task.done():
            rss_task.cancel()
            try:
                await rss_task
            except asyncio.CancelledError:
                pass
```

**Тестирование:**
- Проверка через `uv run --no-project ruff check . --select RUF006`
- Запуск API сервера и graceful shutdown

---

### 🟡 **Приоритет 2: Неиспользуемые аргументы (14 ошибок)**

#### **Фаза 2.1: ARG001 - Unused Function Arguments (10 ошибок)**
**Приоритет:** Средний
**Сложность:** Низкая
**Время:** ~15 мин
**Риск:** Минимальный

**Категории:**

**A) Telegram Bot Handlers (6 ошибок)** - требуют `context` по сигнатуре
- `bot.py:243` - `start_command(context)`
- `bot.py:272` - `help_command(context)`
- `bot.py:281` - `status_command(context)`
- `bot.py:296` - `change_language_command(context)`
- `bot.py:497` - `debug(context)`
- `bot.py:852` - `post_stop(application)`

**Исправление для Telegram handlers:**
```python
# До:
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

# После:
async def start_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
```

**B) API Functions (1 ошибка)**
- `api/routers/rss_items.py:27` - `process_rss_items_results(include_all_translations)`

**Действие:**
- Проверить, планируется ли использование этого параметра
- Если нет - добавить `_` prefix
- Если да - добавить TODO комментарий

**Тестирование:**
- Проверка через `uv run --no-project ruff check . --select ARG001`
- Запуск bot команд и API endpoints

---

#### **Фаза 2.2: ARG004 - Unused Static Method Arguments (3 ошибки)**
**Приоритет:** Средний
**Сложность:** Низкая
**Время:** ~5 мин

**Локации:** (требуется дополнительная проверка)

**Исправление:**
- Добавить `_` prefix к неиспользуемым аргументам
- Или удалить аргумент, если он не требуется интерфейсом

---

#### **Фаза 2.3: ARG002 - Unused Method Argument (1 ошибка)**
**Приоритет:** Средний
**Сложность:** Низкая
**Время:** ~2 мин

---

### 🔵 **Приоритет 3: Упрощения кода (60+ ошибок)**

#### **Фаза 3.1: SIM103 - Needless Bool (4 ошибки)** ✅ Простые
**Приоритет:** Средний
**Сложность:** Низкая
**Время:** ~5 мин
**Риск:** Минимальный

**Локации:**
- `api/database.py:137` - `delete_user()`
- `api/database.py:151` - `activate_user()`
- `api/database.py:485` - `delete_user_rss_feed()`
- `api/deps.py:96` - `is_valid_url()`

**Исправление:**
```python
# До:
if cur.rowcount > 0:
    return True
return False

# После:
return cur.rowcount > 0
```

**Тестирование:**
- Проверка через `uv run --no-project ruff check . --select SIM103`
- Unit тесты для database операций

---

#### **Фаза 3.2: UP046/UP047 - PEP 695 Generic Syntax (3 ошибки)** 🐍 Python 3.13
**Приоритет:** Средний (модернизация)
**Сложность:** Средняя
**Время:** ~10 мин
**Риск:** Средний (новый синтаксис Python 3.13)

**Локации:**
- `api/models.py:48` - `PaginatedResponse(Generic[T])`
- `utils/api.py:32` - `PaginatedResponse(Generic[T])`
- `utils/database.py:28` - `db_operation(func: Callable[P, Awaitable[R]])`

**Исправление (Python 3.13 type parameters):**
```python
# До:
from typing import Generic, TypeVar
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    results: list[T]

# После (Python 3.13):
class PaginatedResponse[T](BaseModel):
    count: int
    results: list[T]
```

**Тестирование:**
- Проверка через `uv run --no-project ruff check . --select UP046,UP047`
- Проверка pydantic совместимости с PEP 695 syntax
- API endpoint responses

---

#### **Фаза 3.3: SIM117 - Multiple With Statements (45 ошибок)** 📦 Массовые изменения
**Приоритет:** Средний
**Сложность:** Низкая (массовая замена)
**Время:** ~30-40 мин
**Риск:** Низкий (простая трансформация)

**Паттерн ошибки:**
```python
# До:
async with pool.acquire() as conn:
    async with conn.cursor() as cur:
        # code...

# После:
async with pool.acquire() as conn, conn.cursor() as cur:
    # code...
```

**Файлы затронуты:**
- `api/database.py` - ~25 функций
- `rss_manager.py` - ~8 функций
- `user_manager.py` - ~6 функций
- `firefeed_dublicate_detector.py` - ~3 функции
- `utils/image.py` - 2 функции

**План исправления:**
1. Начать с `api/database.py` (основной файл, 25 функций)
2. Затем `rss_manager.py`
3. Затем `user_manager.py`
4. Остальные файлы

**Тестирование:**
- Проверка через `uv run --no-project ruff check . --select SIM117`
- Запуск полного набора тестов: `uv run pytest tests/`
- Проверка database операций через API endpoints
- Проверка RSS парсинга и user management

---

#### **Фаза 3.4: Прочие SIM ошибки (9 ошибок)** 🔧 Косметические
**Приоритет:** Низкий
**Сложность:** Низкая
**Время:** ~15 мин

**SIM105 - suppressible-exception (5 ошибок):**
```python
# До:
try:
    clean_text = html.unescape(clean_text)
except Exception:
    pass

# После:
from contextlib import suppress

with suppress(Exception):
    clean_text = html.unescape(clean_text)
```

**SIM108 - if-else-block-instead-of-if-exp (2 ошибки):**
```python
# До:
if conditions:
    where_clause = " AND " + " AND ".join(conditions)
else:
    where_clause = ""

# После:
where_clause = " AND " + " AND ".join(conditions) if conditions else ""
```

**SIM102 - collapsible-if (1 ошибка)**
**SIM110 - reimplemented-builtin (1 ошибка)**

---

#### **Фаза 3.5: Прочие RUF ошибки (3 ошибки)**
**Приоритет:** Низкий
**Сложность:** Низкая
**Время:** ~5 мин

**RUF005 - collection-literal-concatenation (1 ошибка):**
- `api/database.py:1040` - `params + [limit, offset]` → `[*params, limit, offset]`

**RUF059 - unused-unpacked-variable (5 ошибок):**
- `api/routers/rss_items.py:144` - `total_count, results, columns = ...`
- Добавить `_` prefix: `_total_count, results, columns = ...`

---

#### **Фаза 3.6: B007 - Unused Loop Control Variable (1 ошибка)**
**Приоритет:** Низкий
**Сложность:** Тривиальная
**Время:** ~1 мин

**Локация:**
- `firefeed_translator.py:175` - `for i, part in enumerate(sentences):`

**Исправление:**
```python
# До:
for i, part in enumerate(sentences):
    if part.strip() and part[0].isalpha():

# После:
for _i, part in enumerate(sentences):
    if part.strip() and part[0].isalpha():
```

---

## Порядок выполнения (рекомендуемый)

### **Этап 1: Критические исправления** (День 1, ~30 мин)
1. ✅ Фаза 1.1: RUF013 - Implicit Optional (5 ошибок)
2. ✅ Фаза 1.2: RUF012 - Mutable Class Defaults (3 ошибки)
3. ✅ Фаза 1.3: RUF006 - Asyncio Dangling Task (2 ошибки)

**Результат:** 10 критических ошибок устранено, 82 осталось

---

### **Этап 2: Неиспользуемые аргументы** (День 1-2, ~25 мин)
4. ✅ Фаза 2.1: ARG001 - Unused Function Arguments (10 ошибок)
5. ✅ Фаза 2.2: ARG004 - Unused Static Method Arguments (3 ошибки)
6. ✅ Фаза 2.3: ARG002 - Unused Method Argument (1 ошибка)

**Результат:** 14 ошибок устранено, 68 осталось

---

### **Этап 3: Упрощения кода** (День 2-3, ~65 мин)
7. ✅ Фаза 3.1: SIM103 - Needless Bool (4 ошибки) - 5 мин
8. ✅ Фаза 3.6: B007 - Unused Loop Variable (1 ошибка) - 1 мин
9. ✅ Фаза 3.5: Прочие RUF (3 ошибки) - 5 мин
10. ✅ Фаза 3.4: Прочие SIM (9 ошибок) - 15 мин
11. ✅ Фаза 3.2: UP046/UP047 - PEP 695 Generics (3 ошибки) - 10 мин
12. ✅ Фаза 3.3: SIM117 - Multiple With Statements (45 ошибок) - 30-40 мин

**Результат:** 65 ошибок устранено, 3 осталось (ARG004 требует проверки)

---

## Итоговая цель

**Начальное состояние:** 92 ошибки
**Финальная цель:** 0-3 ошибки (только если ARG004 требуют сохранения интерфейса)

**Общее время:** ~2-3 часа работы
**Коммиты:** Рекомендуется разбить на 3-4 коммита по этапам

---

## Рекомендации по тестированию

После каждого этапа:
1. ✅ `uv run --no-project ruff check . --statistics`
2. ✅ `uv run pytest tests/` (если есть тесты)
3. ✅ Ручное тестирование критичных функций:
   - Bot команды: `/start`, `/help`, `/status`
   - API endpoints: GET /rss-items, POST /users
   - Database операции: создание/удаление пользователей
   - RSS парсинг: проверка embeddings процессора

---

## Опциональные безопасные флаги

Ruff предлагает 25 unsafe fixes. Рекомендуется:
- **НЕ использовать** `--unsafe-fixes` без ручной проверки
- Применять unsafe fixes только после ручного review каждого изменения
- Начать с безопасных исправлений из плана выше

---

**Создал:** Claude Code
**Последнее обновление:** 2025-11-12
**Статус:** Готов к выполнению
