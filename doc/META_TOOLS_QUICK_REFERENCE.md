# Meta Tools - Краткий справочник

## 🚀 Быстрый старт

### Установка инструментов
```bash
uv add usort pyrefly libcst codemod
```

## 📦 usort - Сортировка импортов

### Основные команды
```bash
# Сортировать все импорты
uv run usort .

# Проверить без изменений
uv run usort --check .

# Показать diff
uv run usort --diff .

# Сортировать конкретный файл
uv run usort bot.py
```

### В pre-commit
```yaml
- repo: https://github.com/engflow/usort
  rev: v0.6.2
  hooks:
    - id: usort
```

## 🔍 pyrefly - Type Checker от Meta

### Основные команды
```bash
# Инициализация конфигурации (миграция из pyproject.toml)
uv run pyrefly init

# Полная проверка типов
uv run pyrefly check

# Проверка конкретного файла
uv run pyrefly check api/models.py

# Минимальный текстовый вывод
uv run pyrefly check --output-format min-text

# JSON отчёт для анализа
uv run pyrefly check --output-format json > report.json

# Подробный отчёт
uv run pyrefly check --output-format full-text
```

### Конфигурация
pyrefly автоматически мигрирует настройки из `[tool.pyright]` в `[tool.pyrefly]`:

```toml
[tool.pyrefly]
project-includes = ["api", "utils", "*.py"]
project-excludes = ["**/__pycache__", "**/.venv"]
python-version = "3.13.0"
```

## 🔧 libcst - Кастомные трансформации

### Пример скрипта трансформации
```python
#!/usr/bin/env python3
import libcst as cst

class MyTransformer(cst.CSTTransformer):
    def leave_annotation(
        self, original_node: cst.Annotation, updated_node: cst.Annotation
    ) -> cst.Annotation:
        # Ваша логика трансформации
        return updated_node

# Использование
import sys
with open(sys.argv[1]) as f:
    tree = cst.parse_module(f.read())

transformer = MyTransformer()
new_tree = tree.visit(transformer)

with open(sys.argv[1], "w") as f:
    f.write(new_tree.code)
```

## 🎨 codemod - Интерактивные изменения

### Основные команды
```bash
# Интерактивный режим
uv run codemod remove_unused_imports --verbose .

# Превью изменений
uv run codemod mypy/unsafe-overrides --diff .

# Применить изменения
uv run codemod mypy/unsafe-overrides .

# Доступные codemods:
# - mypy/unsafe-overrides
# - remove_unused_imports
# - python/py311-plus
# - and more...
```

## ✅ Полная проверка качества

### Одной командой
```bash
uv run usort . && uv run pyrefly check && uv run ruff check . && uv run pyright && uv run pytest
```

### Пошаговый скрипт
```bash
#!/bin/bash
set -e

echo "🧹 Сортировка импортов (usort)..."
uv run usort check .

echo ""
echo "🔍 Проверка типов (pyrefly)..."
uv run pyrefly check

echo ""
echo "✅ Проверка кода (Ruff)..."
uv run ruff check .

echo ""
echo "🔬 Проверка типов (Pyright)..."
uv run pyright

echo ""
echo "🧪 Запуск тестов..."
uv run pytest
```

### Результаты текущей проверки:
- **usort**: ✅ Все импорты корректно отформатированы
- **pyrefly**: ⚠️ 57 ошибок типов (в основном в api/email_service/sender.py)
- **Ruff**: ✅ All checks passed!
- **Pyright**: ✅ 0 ошибок
- **pytest**: в процессе...
```

## 📝 Типичные сценарии

### Сценарий 1: Новый рефакторинг
```bash
# 1. Сортируем импорты
uv run usort .

# 2. Анализируем что можно улучшить
uv run pyrefly --root . --suggest-imports > suggestions.txt
cat suggestions.txt

# 3. Если нужно, применяем интерактивные изменения
uv run codemod remove_unused_imports --verbose .

# 4. Проверяем результат
uv run ruff check .
uv run pyright
```

### Сценарий 2: Удаление мёртвого кода
```bash
# 1. Полный анализ
uv run pyrefly --root . --json > dead_code.json

# 2. Смотрим отчёт
cat dead_code.json

# 3. Применяем безопасные исправления
uv run pyrefly --root . --fix

# 4. Проверяем
uv run ruff check .
```

### Сценарий 3: Подготовка PR
```bash
# 1. Сортировка
uv run usort .

# 2. Анализ
uv run pyrefly --root . --only-unused-imports

# 3. Проверка
uv run ruff check .
uv run pyright

# 4. Тесты
uv run pytest

# 5. Если всё ок - создаём PR
git add .
git commit -m "feat: ..."

# Или через UV команды
uv run ruff format .
uv run ruff check --fix .
```

## ⚠️ Решение проблем

### usort не сортирует корневые файлы
```bash
# Явно указываем
uv run usort bot.py rss_manager.py firefeed_translator.py
```

### pyrefly находит ложные срабатывания
```bash
# Исключаем файл
uv run pyrefly --root . --exclude "**/dynamic_imports.py"
```

### codemod предлагает нежелательные изменения
```bash
# Используем --diff для превью
uv run codemod mypy/unsafe-overrides --diff .
```

## 📚 Полная документация

Подробный план интеграции: [META_TOOLS_INTEGRATION_PLAN.md](META_TOOLS_INTEGRATION_PLAN.md)

---

**Версия**: 1.0
**Дата**: 2025-11-14
