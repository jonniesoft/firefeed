# Meta Tools Integration Guide - Полное руководство

## Обзор

Этот документ описывает интеграцию и использование инструментов Meta (usort, pyrefly, libcst, codemod) в проекте FireFeed для автоматизации рефакторинга, проверки типов и улучшения качества кода.

---

## 📦 Установленные инструменты

### 1. **usort** - Сортировка импортов
- **Назначение**: Быстрая и точная сортировка импортов
- **Преимущества**: В 3-5 раз быстрее isort, лучше понимает синтаксис Python 3.13
- **Настройка**: В `pyproject.toml` в секции `[tool.usort]`

### 2. **pyrefly** - Проверка типов от Meta
- **Назначение**: Статический анализатор типов, разработанный в Meta
- **Преимущества**: Быстрее pyright, лучше интегрируется с Python 3.13
- **Настройка**: В `pyproject.toml` в секции `[tool.pyrefly]`

### 3. **libcst** - Кастомные трансформации кода
- **Назначение**: Парсинг и трансформация AST кода без потери синтаксиса
- **Использование**: Создание автоматических рефакторингов
- **Примеры**: Исправление типов, добавление комментариев, миграции

### 4. **codemod** - Интерактивные изменения
- **Назначение**: Автоматические рефакторинги на основе preset правил
- **Источник**: Более 100 готовых трансформаций от Meta
- **Безопасность**: Поддержка `--diff` для предварительного просмотра

---

## 🛠️ Скрипты автоматизации

### `/scripts/libcst_transformations.py`

**Назначение**: Кастомные libcst трансформации для FireFeed.

**Возможности**:
- `FixMIMEMultipartAssignment` - Исправляет ошибки типов с MIMEMultipart
- `FixDictAccessAnnotations` - Добавляет type: ignore для TypedDict
- `AddAsyncTypeHints` - Добавляет аннотации для async функций
- `FixStringConcatenation` - Заменяет конкатенацию на f-строки

**Использование**:
```bash
# Применить к одному файлу
python scripts/libcst_transformations.py api/email_service/sender.py

# Применить ко всем файлам в директории
python scripts/libcst_transformations.py api/ --pattern "*.py"

# С другим паттерном
python scripts/libcst_transformations.py . --pattern "*.py"
```

### `/scripts/apply_codemods.py`

**Назначение**: Автоматическое применение безопасных codemod трансформаций.

**Функции**:
1. Удаление неиспользуемых импортов
2. Обновление до Python 3.11+ синтаксиса
3. Проверка unsafe overrides (с предварительным diff)
4. Опциональная проверка орфографии кода

**Использование**:
```bash
# Базовое применение
python scripts/apply_codemods.py

# С проверкой орфографии
python scripts/apply_codemods.py --with-spellcheck

# Для конкретной директории
python scripts/apply_codemods.py api/
```

---

## 📋 Практические сценарии использования

### Сценарий 1: Исправление ошибок типов pyrefly

**Проблема**: pyrefly показывает ошибки в файле

**Решение**:
```bash
# 1. Анализируем ошибки
uv run pyrefly check --output-format full-text > errors.txt
cat errors.txt

# 2. Если ошибки связаны с TypedDict, используем libcst
python scripts/libcst_transformations.py проблемный_файл.py

# 3. Добавляем type: ignore комментарии вручную или через codemod
uv run codemod mypy/unsafe-overrides --diff .
uv run codemod mypy/unsafe-overrides .

# 4. Проверяем результат
uv run pyrefly check проблемный_файл.py
```

### Сценарий 2: Массовый рефакторинг проекта

**Задача**: Применить все безопасные изменения ко всему проекту

**Пошаговый план**:
```bash
# 1. Создаем бэкап
git branch backup-before-refactor
git commit -m "backup: before meta tools refactor"

# 2. Сортируем импорты
uv run usort .

# 3. Применяем codemods
python scripts/apply_codemods.py

# 4. Проверяем изменения
git diff
uv run ruff check .
uv run pyrefly check
uv run pytest

# 5. Фиксируем изменения
git add .
git commit -m "refactor: apply meta tools transformations"
```

### Сценарий 3: Подготовка к миграции на новую версию Python

**Задача**: Обновить код для Python 3.13

**Действия**:
```bash
# 1. Применяем Python 3.11+ трансформации
uv run codemod python/py311-plus .

# 2. Обновляем синтаксис для 3.13 (через libcst)
python scripts/libcst_transformations.py . --pattern "*.py"

# 3. Проверяем совместимость
uv run pyrefly check
uv run ruff check .

# 4. Запускаем тесты
uv run pytest
```

### Сценарий 4: Решение проблем с импортами

**Проблема**: Неиспользуемые импорты или неправильный порядок

**Решение**:
```bash
# 1. Сортируем импорты
uv run usort .

# 2. Удаляем неиспользуемые
uv run codemod remove_unused_imports .

# 3. Проверяем результат
uv run ruff check .
uv run usort --check .
```

---

## 🎯 Интеграция в GitHub Actions

Пример workflow для CI/CD:

```yaml
name: Code Quality Checks

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v2

      - name: Install dependencies
        run: uv sync

      - name: Check imports with usort
        run: uv run usort --check .

      - name: Type check with pyrefly
        run: uv run pyrefly check

      - name: Lint with ruff
        run: uv run ruff check .

      - name: Apply codemods (safe only)
        run: python scripts/apply_codemods.py

      - name: Run tests
        run: uv run pytest
```

---

## 📊 Отчеты и метрики

### Генерация полного отчета

```bash
# Создаем скрипт отчета
cat > generate_report.sh << 'EOF'
#!/bin/bash
echo "=== Отчет о качестве кода ==="
echo ""

echo "1️⃣ Импорты (usort)"
uv run usort --check . && echo "✅ Все импорты корректны" || echo "❌ Есть проблемы"

echo ""
echo "2️⃣ Типы (pyrefly)"
ERROR_COUNT=$(uv run pyrefly check 2>&1 | grep -c "error:" || echo "0")
echo "   Найдено ошибок: $ERROR_COUNT"

echo ""
echo "3️⃣ Стиль (ruff)"
uv run ruff check . --statistics

echo ""
echo "4️⃣ Тесты (pytest)"
uv run pytest --tb=short -q

echo ""
echo "=== Конец отчета ==="
EOF

chmod +x generate_report.sh
./generate_report.sh
```

### Сохранение отчета в файл

```bash
uv run pyrefly check --output-format json > pyrefly_report.json
uv run ruff check . --output-format=json > ruff_report.json
```

---

## ⚙️ Конфигурация

### pyproject.toml

**usort**:
```toml
[tool.usort]
profile = "black"
known_first_party = ["api", "utils", "bot", "config"]
force_single_line = false
preserve_comments = true
```

**pyrefly**:
```toml
[tool.pyrefly]
project-includes = ["api", "utils", "*.py"]
project-excludes = ["**/__pycache__", "**/.venv"]
python-version = "3.13.0"
python-platform = "linux"
infer-with-first-use = false

[tool.pyrefly.errors]
missing-import = "error"
```

**ruff**:
```toml
[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "B", "C4", "UP", "ARG", "SIM", "TCH", "PTH", "RUF"]
ignore = ["E501", "B008", "B904", "UP007", "RUF001", "RUF002", "RUF003"]
```

---

## 🚨 Часто встречающиеся ошибки

### Ошибка: "Cannot set item in MIMEMultipart"

**Причина**: pyrefly не может вывести тип для MIMEMultipart.__setitem__

**Решение**:
```python
message["Subject"] = value  # type: ignore[assignment]
```

### Ошибка: "Argument ... is not assignable to parameter ..."

**Причина**: TypedDict доступ с неопределенным типом

**Решение**:
```python
self.config["key"]  # type: ignore[typeddict-item]
```

### Ошибка: "unsupported-operation" с MIMEMultipart

**Причина**: Проблема с типами в email.mime

**Решение**: Использовать `typing.cast` или `# type: ignore`

---

## 🔧 Расширение функциональности

### Создание новой libcst трансформации

```python
class MyCustomTransformer(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> cst.FunctionDef:
        """Ваша логика трансформации"""
        # Добавляем type hint если его нет
        if not original_node.returns:
            returns = cst.Annotation(annotation=cst.Name("bool"))
            return original_node.with_changes(returns=returns)
        return original_node
```

### Создание нового codemod правила

```bash
# Создаем правило в codemod/ directory
mkdir -p codemod/my_rules
touch codemod/my_rules/__init__.py
# Добавляем правило
```

---

## 📚 Полезные ссылки

- [usort documentation](https://github.com/engflow/usort)
- [pyrefly documentation](https://github.com/Meta/pyrefly)
- [libcst documentation](https://libcst.readthedocs.io/)
- [codemod documentation](https://github.com/facebook/codemod)

---

## ✅ Чек-лист перед коммитом

- [ ] Импорты отсортированы: `uv run usort --check .`
- [ ] Нет ошибок типов: `uv run pyrefly check`
- [ ] Код соответствует стандартам: `uv run ruff check .`
- [ ] Все тесты проходят: `uv run pytest`
- [ ] Применены безопасные codemods: `python scripts/apply_codemods.py --dry-run`
- [ ] Проверены изменения: `git diff`

---

**Версия**: 1.0
**Дата**: 2025-11-14
**Проект**: FireFeed
