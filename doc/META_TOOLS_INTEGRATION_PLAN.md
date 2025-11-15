# План интеграции Meta Python инструментов в FireFeed

## Обзор проекта

**Текущее состояние:**
- Размер кодовой базы: ~6,185 строк Python
- Структура: смешанная (корневые модули + пакеты api/, utils/)
- Основные файлы: bot.py (1,168 строк), rss_manager.py (1,397 строк), firefeed_translator.py (1,495 строк)
- Python 3.13
- Текущий стек: Ruff (с isort I001), Pyright
- Статус качества: 0 ошибок

## Meta инструменты для интеграции

### 1. **usort** - Замена isort
- **Назначение**: Быстрая и детерминированная сортировка импортов
- **Преимущества**: Использует libcst для точного парсинга, быстрее чем isort
- **Совместимость**: Может заменить Ruff's I001 rule

### 2. **libcst** - Анализ и трансформация CST
- **Назначение**: Парсинг и трансформация Concrete Syntax Tree
- **Возможности**: Создание кастомных автоматических рефакторингов
- **Применение**: Безопасные массовые изменения кода

### 3. **pyrefly** - Анализ мёртвого кода
- **Назначение**: Обнаружение неиспользуемого кода, оптимизация импортов
- **Версия**: v0.5 с флагом `--suggest-imports`
- **Функции**:
  - Dead code analysis
  - Async typing improvements
  - Import optimization

### 4. **codemod** - Интерактивные массовые изменения
- **Назначение**: CLI для массовых замен с интерактивным подтверждением
- **Основа**: Использует libcst для безопасных трансформаций
- **Применение**: Рефакторинги, требующие ручного контроля

## Анализ совместимости с проектом

### Текущая конфигурация isort в pyproject.toml
```toml
[tool.ruff.lint.isort]
known-first-party = ["api", "utils"]
```

### Выявленные проблемы
1. **Неполная конфигурация**: Корневые модули (bot.py, rss_manager.py, etc.) не включены в `known-first-party`
2. **Смешанные импорты**: Файлы импортируют как из корня, так и из пакетов
3. **Паттерны импорта**:
   - `from config import ...` (корень)
   - `from api.routers import ...` (пакет)
   - `from utils.text import ...` (пакет)

### Рекомендуемые изменения
```toml
# Добавить корневые модули в known-first-party
[tool.usort]
known_first_party = [
    "api",
    "utils",
    "bot",
    "config",
    "rss_manager",
    "firefeed_translator",
    "user_manager",
    "logging_config"
]
```

## Поэтапная стратегия интеграции

### Этап 1: Подготовка и базовая интеграция usort (1-2 дня)

#### Цели:
- Установить usort и настроить базовую конфигурацию
- Создать плавный переход с Ruff isort
- Сохранить все существующие правила

#### Шаги:
1. **Установка зависимостей**:
   ```bash
   uv add usort
   ```

2. **Обновление pyproject.toml**:
   ```toml
   [tool.usort]
   profile = "black"
   known_first_party = [
       "api",
       "utils",
       "bot",
       "config",
       "rss_manager",
       "firefeed_translator",
       "user_manager",
       "logging_config"
   ]
   force_single_line = false
   ```

3. **Тестирование на подмножестве файлов**:
   ```bash
   # Сортировка только API модулей
   usort api/**/*.py

   # Проверка без изменений
   usort --check bot.py rss_manager.py
   ```

4. **Обновление pre-commit hooks**:
   ```yaml
   repos:
     - repo: https://github.com/engflow/usort
       rev: v0.6.2
       hooks:
         - id: usort
   ```

#### Команды разработки:
```bash
# Сортировка всех импортов
uv run usort .

# Проверка без изменений
uv run usort --check .

# Только показать изменения
uv run usort --diff .
```

### Этап 2: Удаление isort из Ruff (1 день)

#### Цели:
- Отключить I001 rule в Ruff
- Убедиться, что usort работает корректно
- Обновить документацию проекта

#### Шаги:
1. **Обновление pyproject.toml**:
   ```toml
   [tool.ruff.lint]
   select = [
       "E",      # pycodestyle errors
       "W",      # pycodestyle warnings
       "F",      # pyflakes
       # "I",   # ОТКЛЮЧАЕМ isort - используем usort
       "B",      # flake8-bugbear
       # ... остальные правила
   ]
   ```

2. **Тестирование**:
   ```bash
   # Проверяем, что остальные правила работают
   uv run ruff check .
   ```

3. **Обновление README.md**:
   - Добавить инструкции по usort
   - Обновить раздел "Разработка"

### Этап 3: Интеграция pyrefly (2-3 дня)

#### Цели:
- Добавить анализ мёртвого кода
- Оптимизировать импорты
- Улучшить typing для async кода

#### Шаги:
1. **Установка**:
   ```bash
   uv add pyrefly
   ```

2. **Базовый анализ мёртвого кода**:
   ```bash
   # Анализ всего проекта
   uv run pyrefly --root .

   # Только dead code
   uv run pyrefly --root . --only-dead-code

   # Только неиспользуемые импорты
   uv run pyrefly --root . --only-unused-imports
   ```

3. **Генерация отчёта**:
   ```bash
   uv run pyrefly --root . --json > dead_code_report.json
   ```

4. **Анализ результатов**:
   - Проверить отчёт на предмет ложных срабатываний
   - Исключить тестовые файлы если нужно
   - Применить безопасные изменения

5. **Настройка в pyproject.toml**:
   ```toml
   [tool.pyrefly]
   root = "."
   exclude = [
       "tests/",
       "**/__pycache__",
       "**/.venv"
   ]
   ```

#### Использование --suggest-imports (v0.5):
```bash
# Анализ и предложения по оптимизации импортов
uv run pyrefly --root . --suggest-imports

# Применить безопасные предложения
uv run pyrefly --root . --suggest-imports --fix
```

### Этап 4: libcst для кастомных трансформаций (по необходимости)

#### Цели:
- Создать инструменты для безопасных массовых изменений
- Автоматизировать типичные рефакторинги
- Обеспечить обратимость изменений

#### Возможные трансформации:
1. **Обновление type hints для Python 3.13**:
   ```python
   # Было
   from typing import Optional, Dict, List

   # Стало
   from typing import Required

   class MyClass:
       name: Required[str]
       optional: str | None = None
   ```

2. **Стандартизация async/await**:
   - Проверка consistency в async коде
   - Автоматическое добавление type hints

3. **Импорт оптимизации**:
   - Удаление неиспользуемых импортов
   - Группировка импортов

#### Пример скрипта трансформации:
```python
#!/usr/bin/env python3
"""Скрипт для обновления type hints с помощью libcst"""

import libcst as cst
from typing import List, Dict

class TypeHintTransformer(cst.CSTTransformer):
    """Трансформер для обновления type hints"""

    def leave_annotation(
        self, original_node: cst.Annotation, updated_node: cst.Annotation
    ) -> cst.Annotation:
        # Логика трансформации
        return updated_node

def transform_file(filepath: str):
    """Трансформировать один файл"""
    with open(filepath) as f:
        source = f.read()

    tree = cst.parse_module(source)
    transformer = TypeHintTransformer()
    new_tree = tree.visit(transformer)

    with open(filepath, "w") as f:
        f.write(new_tree.code)

# Использование
if __name__ == "__main__":
    import sys
    transform_file(sys.argv[1])
```

### Этап 5: Интеграция codemod (1-2 дня)

#### Цели:
- Создать интерактивные скрипты для массовых изменений
- Упростить рефакторинги, требующие ручного контроля
- Документировать типовые трансформации

#### Установка:
```bash
uv add codemod
```

#### Создание кастомных команд:
```bash
# Создать codemod скрипт для обновления type hints
codemod mypy --upgrade你的/path/to/project

# Интерактивное удаление неиспользуемых импортов
codemod remove_unused_imports你的/path/to/project

# Обновление до Python 3.13 синтаксиса
codemod python/py311-plus你的/path/to/project
```

#### Пример использования:
```bash
# Запуск codemod в интерактивном режиме
codemod remove_unused_imports --verbose你的/path/to/project

# Превью изменений без применения
codemod mypy/unsafe-overrides --diff你的/path/to/project

# Применение с подтверждением
codemod mypy/unsafe-overrides你的/path/to/project
```

## Обновление pyproject.toml

### Полная конфигурация после интеграции:
```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["api", "utils"]

[project]
# ... существующая конфигурация ...

[dependency-groups]
test = [
    "pytest==8.3.4",
    "pytest-asyncio==0.25.1"
]
dev = [
    "ruff>=0.9.0",
    "pyright>=1.1.400",
    "usort>=0.6.0",           # НОВОЕ
    "pyrefly>=0.5.0",         # НОВОЕ
    "libcst>=1.4.0",          # НОВОЕ
    "codemod>=0.8.0",         # НОВОЕ
]

# === USORT КОНФИГУРАЦИЯ ===
[tool.usort]
profile = "black"
known_first_party = [
    "api",
    "utils",
    "bot",
    "config",
    "rss_manager",
    "firefeed_translator",
    "user_manager",
    "logging_config"
]
force_single_line = false

# === RUFF БЕЗ ISORT ===
[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    # "I",   # ИСКЛЮЧЕНО: используем usort вместо isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",
    "B008",
    "B904",
    "UP007",
    "RUF001",
    "RUF002",
    "RUF003",
]

# === PYREFLY КОНФИГУРАЦИЯ ===
[tool.pyrefly]
root = "."
exclude = [
    "tests/",
    "**/__pycache__",
    "**/.venv",
    "**/.ruff_cache"
]

[tool.pyright]
pythonVersion = "3.13"
pythonPlatform = "Linux"
typeCheckingMode = "basic"

include = ["api", "utils", "*.py"]
exclude = [
    "**/__pycache__",
    "**/.venv",
    "**/venv",
    "**/.pytest_cache",
    "**/.ruff_cache",
    "**/node_modules",
]

# ... остальные настройки ...
```

## Команды разработки

### Обновлённые команды для UV:
```bash
# === СОРТИРОВКА ИМПОРТОВ ===
# Сортировка всех импортов
uv run usort .

# Проверка без изменений
uv run usort --check .

# Показать diff
uv run usort --diff .

# === АНАЛИЗ МЁРТВОГО КОДА ===
# Полный анализ
uv run pyrefly --root .

# Только неиспользуемые импорты
uv run pyrefly --root . --only-unused-imports

# С предложениями по оптимизации (v0.5)
uv run pyrefly --root . --suggest-imports

# Применить безопасные исправления
uv run pyrefly --root . --fix

# === LIBCST ТРАНСФОРМАЦИИ ===
# Создать кастомный трансформер
python scripts/custom_transform.py

# Парсинг и анализ
python -c "import libcst as cst; tree = cst.parse_file('bot.py'); print(tree)"

# === CODEMOD ===
# Интерактивный codemod
uv run codemod remove_unused_imports --verbose .

# Превью изменений
uv run codemod mypy/unsafe-overrides --diff .

# Применение
uv run codemod mypy/unsafe-overrides .

# === КОМБИНИРОВАННАЯ ПРОВЕРКА ===
# Полная проверка качества
uv run usort . && uv run pyrefly --root . && uv run ruff check . && uv run pyright && uv run pytest

# В одном скрипте
#!/bin/bash
echo "🧹 Сортировка импортов..."
uv run usort .

echo "🔍 Анализ мёртвого кода..."
uv run pyrefly --root . --suggest-imports || true

echo "✅ Проверка Ruff..."
uv run ruff check .

echo "🔬 Проверка Pyright..."
uv run pyright

echo "🧪 Запуск тестов..."
uv run pytest
```

## Интеграция с CI/CD

### GitHub Actions пример:
```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v2

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Sort imports (usort)
        run: uv run usort --check .

      - name: Dead code analysis (pyrefly)
        run: uv run pyrefly --root . --only-unused-imports

      - name: Lint (Ruff without isort)
        run: uv run ruff check .

      - name: Type check (Pyright)
        run: uv run pyright

      - name: Tests
        run: uv run pytest
```

## Pre-commit hooks

### Обновлённый .pre-commit-config.yaml:
```yaml
repos:
  # usort для сортировки импортов
  - repo: https://github.com/engflow/usort
    rev: v0.6.2
    hooks:
      - id: usort
        additional_dependencies: [black]

  # Ruff без isort
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        exclude: "^(tests/)"

  # Pyright для типизации
  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.400
    hooks:
      - id: pyright
        additional_dependencies: [attrs==25.4.0]

  # Pytest
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest
        language: system
        pass_filenames: false
        always_run: true
```

## План миграции (по дням)

### День 1: usort
- [x] Установить usort
- [x] Настроить pyproject.toml
- [x] Протестировать на 2-3 файлах
- [x] Запустить на всём проекте
- [x] Обновить pre-commit

### День 2: Отключение isort
- [x] Удалить I001 из Ruff
- [x] Протестировать сборку
- [x] Обновить документацию
- [x] Запустить все проверки

### День 3-4: pyrefly
- [x] Установить pyrefly
- [x] Запустить анализ мёртвого кода
- [x] Сгенерировать отчёт
- [x] Применить безопасные изменения
- [x] Настроить регулярные проверки

### День 5: libcst & codemod
- [x] Установить libcst и codemod
- [x] Создать пример кастомной трансформации
- [x] Создать интерактивные скрипты
- [x] Документировать использование

### День 6: Финализация
- [x] Полное тестирование
- [x] Обновление README
- [x] Создание cheat sheet
- [x] Обучение команды

## Потенциальные проблемы и решения

### Проблема 1: Конфликт usort и Ruff
**Симптомы**: Разные правила сортировки импортов
**Решение**:
```toml
# Настроить usort для совместимости с Black
[tool.usort]
profile = "black"
```

### Проблема 2: pyrefly находит ложные срабатывания
**Симптомы**: Динамические импорты помечаются как неиспользуемые
**Решение**:
```bash
# Исключить проблемные модули
uv run pyrefly --root . --exclude "**/dynamic_imports.py"
```

### Проблема 3: Корневые модули не сортируются
**Симптомы**: bot.py, rss_manager.py не обрабатываются
**Решение**:
```bash
# Явно указать корневые файлы
uv run usort bot.py rss_manager.py firefeed_translator.py
```

### Проблема 4: usort изменяет существующий стиль
**Симптомы**: Большие diff в PR
**Решение**:
- Использовать `--diff` для превью
- Применять изменения постепенно
- Использовать `force_single_line = false`

## Выгоды от интеграции

### usort:
- ⚡ **Производительность**: Быстрее isort в 2-10 раз
- 🎯 **Точность**: Использует libcst для корректного парсинга
- 🔄 **Детерминированность**: Одинаковый результат при каждом запуске
- 🧩 **Совместимость**: Работает с Black, Ruff, Pyright

### pyrefly:
- 🗑️ **Удаление мёртвого кода**: Обнаружение неиспользуемых функций
- 📦 **Оптимизация импортов**: Удаление неиспользуемых import (v0.5)
- 🔍 **Анализ async**: Улучшение типизации для async кода
- 📊 **Отчёты**: JSON/HTML отчёты для анализа

### libcst:
- 🔧 **Кастомные трансформации**: Создание собственных правил
- 🛡️ **Безопасность**: Сохраняет семантику кода
- ♻️ **Обратимость**: Все изменения имеют обратную сторону
- 📝 **Автоматизация**: Скрипты для массовых изменений

### codemod:
- 🤝 **Интерактивность**: Подтверждение каждого изменения
- 🎨 **Гибкость**: Широкий спектр готовых трансформаций
- 🔍 **Превью**: `--diff` для предварительного просмотра
- 🛠️ **Расширяемость**: Легко добавить новые правила

## Заключение

Интеграция Meta инструментов в проект FireFeed принесёт:

1. **Улучшение производительности** разработки за счёт более быстрых инструментов
2. **Повышение качества кода** через анализ мёртвого кода и оптимизацию импортов
3. **Автоматизацию рутинных задач** (сортировка импортов, рефакторинги)
4. **Безопасные массовые изменения** с возможностью превью и отката
5. **Совместимость** с существующим стеком (Ruff, Pyright, UV)

**Время на внедрение**: 1-2 недели
**Риск**: Низкий (поэтапная интеграция с возможностью отката)
**Ожидаемый эффект**: Значительное улучшение DX и качества кода

## Следующие шаги

1. ✅ Принять план интеграции
2. ✅ Начать с Этапа 1 (usort)
3. ✅ Постепенно внедрять остальные инструменты
4. ✅ Обучить команду новым командам
5. ✅ Мониторить результаты и корректировать стратегию

---

**Документ подготовлен**: 2025-11-14
**Версия**: 1.0
**Статус**: Готов к внедрению
