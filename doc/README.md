# 📚 Документация FireFeed

Полная документация проекта FireFeed.

---

## 🔗 Навигация

### Meta Tools - Инструменты качества кода

- **[Meta Tools Integration Guide](META_TOOLS_INTEGRATION_GUIDE.md)** - Полное руководство по интеграции usort, pyrefly, libcst, codemod
- **[Meta Tools Quick Reference](META_TOOLS_QUICK_REFERENCE.md)** - Краткий справочник команд
- **[Meta Tools Integration Plan](META_TOOLS_INTEGRATION_PLAN.md)** - План интеграции инструментов
- **[Stage 3 Completion Summary](STAGE_3_COMPLETION_SUMMARY.md)** - Отчет о завершении этапа 3

### Архитектура и развертывание

- **[Docker Compose Guide](DOCKER_COMPOSE.md)** - Руководство по развертыванию с Docker
- **[Email Setup](EMAIL_SETUP.md)** - Настройка email сервиса

### Разработка

- **[Contributing Guide](CONTRIBUTING.md)** - Руководство для контрибьюторов
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Кодекс поведения
- **[Agents Documentation](AGENTS.md)** - Документация по агентам

---

## 🚀 Быстрый старт

### Проверка качества кода

```bash
# Полная проверка (рекомендуется)
./scripts/test_meta_tools.sh

# Или пошагово:
uv run usort check .
uv run pyrefly check
uv run ruff check .
uv run pytest
```

### Применение автоисправлений

```bash
# Применить codemods
python scripts/apply_codemods.py

# Сортировка импортов
uv run usort .

# Исправление стиля кода
uv run ruff check --fix .
```

---

## 📊 Инструменты качества

| Инструмент | Версия | Назначение |
|------------|--------|------------|
| usort | 1.1.0 | Сортировка импортов |
| pyrefly | 0.41.2 | Проверка типов |
| libcst | 1.8.6 | Трансформации кода |
| codemod | 1.0.0 | Автоматические рефакторинги |

Подробнее в [Meta Tools Integration Guide](META_TOOLS_INTEGRATION_GUIDE.md).

---

## 🛠️ Скрипты автоматизации

- `/scripts/libcst_transformations.py` - libcst трансформации
- `/scripts/apply_codemods.py` - применение codemods
- `/scripts/test_meta_tools.sh` - тестирование интеграции

---

**Проект**: FireFeed
**Дата**: 2025-11-14
