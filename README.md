# FireFeed - AI-powered RSS aggregator and parser

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![Podman](https://img.shields.io/badge/Podman-Supported-blue.svg)](https://podman.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](https://github.com/yuremweiland/firefeed/actions)

Современный новостной агрегатор с поддержкой искусственного интеллекта для автоматического сбора, обработки и распространения новостей на нескольких языках.

**Официальный сайт**: https://firefeed.jonniesoft.com

## Содержание

- [Обзор проекта](#обзор-проекта)
- [Основные возможности](#основные-возможности)
- [Технический стек](#технический-стек)
- [Архитектура](#архитектура)
- [Установка и запуск](#установка-и-запуск)
- [Конфигурация](#конфигурация)
- [API документация](#api-документация)
- [Разработка](#разработка)
  - [Workflow проверки качества кода](#workflow-проверки-качества-кода)
- [Лицензия](#лицензия)

## Обзор проекта

FireFeed - это высокопроизводительная система для автоматического сбора, обработки и распространения новостного контента. Проект использует современные технологии машинного обучения для интеллектуальной обработки текста и обеспечивает многоязычную поддержку для международной аудитории.

## Основные возможности

### AI-powered обработка контента

- **Автоматический перевод новостей** на 4 языка (русский, немецкий, французский, английский) с использованием современных моделей машинного обучения (Helsinki-NLP OPUS-MT, M2M100)
- **Обнаружение дубликатов** с помощью семантического анализа и векторных эмбеддингов (Sentence Transformers)
- **Интеллектуальная обработка изображений** с автоматическим извлечением и оптимизацией

### Многоязычная поддержка

- Полностью локализованный Telegram-бот с поддержкой 4 языков
- REST API с многоязычным интерфейсом
- Адаптивная система переводов с учетом терминологии

### Гибкая система RSS

- **Автоматический парсинг** более 50 RSS-лент различных источников
- **Категоризация новостей** по темам (мировые новости, технологии, спорт, экономика и др.)
- **Персонализированные подписки** пользователей на категории и источники
- **Пользовательские RSS-ленты** - возможность добавления собственных источников

### Безопасная архитектура

- **JWT-аутентификация** для API
- **Шифрование паролей** с использованием bcrypt
- **Валидация email** с кодом подтверждения
- **Защищенное хранение секретов** через переменные окружения

### Высокая производительность

- **Асинхронная архитектура** на базе asyncio
- **Пул соединений PostgreSQL** для эффективной работы с БД
- **Очереди задач** для параллельной обработки переводов
- **Кэширование моделей** ML для оптимизации памяти

## Технический стек

### Backend
- Python 3.13 с asyncio
- FastAPI для REST API
- PostgreSQL с pgvector для семантического поиска
- aiopg для асинхронных запросов к БД

### AI/ML
- Transformers (Hugging Face)
- Sentence Transformers для эмбеддингов
- SpaCy для обработки текста
- Torch для вычислений

### Интеграции
- Telegram Bot API
- SMTP для email-уведомлений
- Webhook-поддержка

### Инфраструктура
- Podman-контейнеризация
- systemd для управления сервисами
- nginx для проксирования

## Архитектура

Проект состоит из нескольких ключевых компонентов:

1. **Telegram Bot** (`bot.py`) - основной интерфейс взаимодействия с пользователями
2. **RSS Parser Service** (`rss_parser.py`) - фоновая служба парсинга RSS-лент
3. **REST API** (`api/main.py`) - веб-API для внешних интеграций
4. **Translation Engine** (`firefeed_translator.py`) - система переводов с кэшированием
5. **Duplicate Detector** (`firefeed_dublicate_detector.py`) - обнаружение дубликатов через ML
6. **User Management** (`user_manager.py`) - управление пользователями и подписками

### Масштабируемость и надежность

- **Горизонтальное масштабирование** через микросервисную архитектуру
- **Отказоустойчивость** с автоматическими перезапусками и логированием
- **Мониторинг производительности** с подробной телеметрией
- **Graceful shutdown** для корректного завершения работы

## Установка и запуск

### Предварительные требования

- **Python 3.13** (строго рекомендуется)
  - Python 3.14 пока не поддерживается из-за отсутствия wheels для `torch==2.8.0`
  - Более старые версии не тестировались с текущими зависимостями
- UV package manager (установка, зафиксированная версия 0.9.8: `curl -LsSf https://astral.sh/uv/0.9.8/install.sh | sh`) — версия закреплена как `0.9.8` для совпадения с Dockerfile; при обновлении, обновляйте и Dockerfile, и README синхронно, чтобы избежать дрейфа версий.
- PostgreSQL 12+ с расширением pgvector
- Токен Telegram Bot API

**Важные замечания по зависимостям:**
- В проекте используется `psycopg2-binary==2.9.10` вместо `psycopg2==2.9.10`
  - **Причина:** `psycopg2` требует компиляции из исходников и наличия PostgreSQL development headers
  - `psycopg2-binary` предоставляет готовые скомпилированные wheels для всех платформ
  - Для production окружений рекомендуется `psycopg2-binary` для упрощения развертывания
  - Для локальной разработки `psycopg2-binary` работает идентично `psycopg2`

### Установка зависимостей

```bash
uv pip install -r requirements.txt
```

**Примечание**: Миграция на `pyproject.toml` и `uv.lock` — Target: Q1 2026; trigger: после стабильного релиза 1.0 или стабилизации зависимостей в CI. До миграции используйте `requirements.txt`; устаревание: `requirements.txt` поддерживается до Q2 2026 или до завершения миграции. Прогресс: https://github.com/yuremweiland/firefeed/issues, https://github.com/yuremweiland/firefeed/projects.

### Базовый запуск

```bash
# Создание виртуального окружения (UV управляет этим автоматически)
uv venv

# UV автоматически управляет виртуальным окружением
# Запуск Telegram бота
uv run python bot.py
# или просто
uv run bot.py
```

### Запуск через скрипты

```bash
# Дать права на выполнение
chmod +x ./run_bot.sh
chmod +x ./run_api.sh
chmod +x ./scripts/start-database.sh

# Запуск БД (PostgreSQL + Redis)
./scripts/start-database.sh

# Запуск бота
./run_bot.sh

# Запуск API
./run_api.sh
```

**Примечание**: Скрипт `./scripts/start-database.sh` автоматически настраивает Podman и запускает только необходимые для разработки сервисы (БД и Redis).

### Запуск через Podman

Проект поддерживает контейнеризацию и запуск через Podman с использованием multi-stage сборки.

**Требования:**
- Podman 4+ (рекомендуется 5+)

**Сборка образа:**

```bash
# Соберите образ (из Dockerfile)
podman build -t firefeed:latest -f Dockerfile .
```

**Примечание**: Dockerfile содержит расширения синтаксиса Dockerfile 1.7 (например, `RUN --mount=type=cache`). В большинстве окружений Podman образ собирается корректно; если ваша версия Podman/Buildah не поддерживает эти расширения и сборка падает, попробуйте:
- выполнить сборку без кэша: `podman build --no-cache -t firefeed:latest -f Dockerfile .`
- или временно собрать образ в Docker и запускать в Podman

**Запуск контейнера:**

```bash
# Запуск API
podman run -d -p 8000:8000 --env-file .env --name firefeed-api firefeed:latest

# Запуск бота (переопределение CMD)
podman run -d --env-file .env --name firefeed-bot firefeed:latest python bot.py

# Запуск RSS парсера
podman run -d --env-file .env --name firefeed-parser firefeed:latest python rss_parser.py
```

### Запуск через podman-compose

В репозитории используется файл `docker-compose.yml`, совместимый с `podman-compose`.

#### ⚙️ Настройка Podman для коротких имен образов

Podman требует полные доменные имена для образов или настроенный `registries.conf`. Для вашего удобства:

1. **Локальный файл конфигурации**: `.config/containers/registries.conf`
   - Автоматически копируется в `~/.config/containers/registries.conf` при первом запуске
   - Позволяет использовать короткие имена образов (например, `redis:7-alpine`)
   - Указывает Docker Hub как основной registry для поиска образов

2. **Автоматический запуск БД**: скрипт `./scripts/start-database.sh`
   - Создает и настраивает registries.conf
   - Запускает только PostgreSQL и Redis
   - Ждет готовности БД перед завершением
   - Автоматически получает параметры из `.env`

#### 🚀 Запуск базы данных

**Быстрый способ (рекомендуется):**

```bash
# Запустить только БД и Redis
./scripts/start-database.sh

# Проверить статус
podman-compose ps
```

**Полный запуск всех сервисов:**

```bash
# Поднять все сервисы в фоне
podman-compose up -d

# Проверить состояние
podman-compose ps

# Остановить и удалить
podman-compose down
```

**Остановка только БД:**

```bash
# Остановить PostgreSQL и Redis
podman-compose stop db redis
```

## Конфигурация

### Переменные окружения

Создайте файл `.env` в корневой директории проекта:

```env
DATABASE_URL=postgresql://user:password@localhost/firefeed
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
JWT_SECRET_KEY=your_jwt_secret_key
SMTP_SERVER=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
```

### Конфигурация контейнеров

Для корректной работы Podman с короткими именами образов в проекте создан файл `.config/containers/registries.conf`:

```ini
[registries.search]
registries = ['docker.io']

[registries.insecure]
registries = []

[registries.block]
registries = []
```

**Что это делает:**
- Указывает Podman искать образы по коротким именам в Docker Hub (`docker.io`)
- Позволяет использовать `redis:7-alpine` вместо `docker.io/library/redis:7-alpine`
- Автоматически копируется в `~/.config/containers/registries.conf` скриптом `./scripts/start-database.sh`

**Почему это нужно:**
По умолчанию Podman блокирует короткие имена образов из соображений безопасности (предотвращение атак типа "image hijacking"). Этот файл конфигурации явно разрешает использование Docker Hub как доверенного registry.

### Systemd сервисы

Для продакшн-окружения рекомендуется использовать systemd сервисы.

**Сервис Telegram-бота** (`/etc/systemd/system/firefeed-bot.service`):

```ini
[Unit]
Description=FireFeed Telegram Bot Service
After=network.target

[Service]
Type=simple
User=firefeed
Group=firefeed
WorkingDirectory=/var/www/firefeed/data/integrations/telegram

ExecStart=/var/www/firefeed/data/integrations/telegram/run_bot.sh

Restart=on-failure
RestartSec=10

TimeoutStopSec=30
KillMode=mixed
KillSignal=SIGTERM
SendSIGKILL=yes

[Install]
WantedBy=multi-user.target
```

**Сервис API** (`/etc/systemd/system/firefeed-api.service`):

```ini
[Unit]
Description=Firefeed News API (FastAPI)
After=network.target
After=postgresql@17-main.service
Wants=postgresql@17-main.service

[Service]
Type=simple
User=firefeed
Group=firefeed

WorkingDirectory=/var/www/firefeed/data/integrations/telegram
ExecStart=/var/www/firefeed/data/integrations/telegram/run_api.sh

Restart=always
RestartSec=5

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Nginx конфигурация

Пример конфигурации для работы через webhook и FastAPI:

```nginx
upstream fastapi_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your_domain.com;

    location /webhook {
        proxy_pass http://127.0.0.1:5000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/ {
        proxy_pass http://fastapi_app;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## API документация

После запуска API сервера документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Основные endpoints:

- `GET /api/v1/news` - получение списка новостей
- `POST /api/v1/users/register` - регистрация пользователя
- `GET /api/v1/subscriptions` - управление подписками

## Разработка

### Установка для разработки

```bash
# Клонируйте репозиторий c GitHub
git clone https://github.com/yuremweiland/firefeed.git
# или GitVerse
git clone https://gitverse.ru/yuryweiland/firefeed.git
cd firefeed

# Установка зависимостей
uv pip install -r requirements.txt
```

**Примечание**: Миграция на `pyproject.toml` и `uv.lock` — Target: Q1 2026; trigger: после стабильного релиза 1.0 или стабилизации зависимостей в CI. До миграции используйте `requirements.txt`; устаревание: `requirements.txt` поддерживается до Q2 2026 или до завершения миграции. Прогресс: https://github.com/yuremweiland/firefeed/issues, https://github.com/yuremweiland/firefeed/projects.

### Работа с UV

UV - это современный быстрый менеджер пакетов Python от Astral, который значительно ускоряет установку зависимостей и обеспечивает детерминированные сборки.

**Основные команды UV:**

```bash
# Установка зависимостей (текущий способ)
uv pip install -r requirements.txt

# После миграции на pyproject.toml:
# uv sync                 # Установка зависимостей
# uv add <package>        # Добавление нового пакета
# uv lock                 # Обновление lockfile

# Запуск скриптов в виртуальном окружении
uv run python script.py
```

**Преимущества UV:**

- **Быстрая установка зависимостей**: особенно важно для ML-библиотек (torch, transformers, sentence-transformers)
- **Детерминированные сборки**: через `uv.lock` обеспечивается воспроизводимость окружения
- **Автоматическое управление виртуальными окружениями**: не нужно вручную активировать venv

**Совместимость с pip**: В случаях, когда нужен fallback, можно продолжать использовать pip с `requirements.txt`.

### Запуск тестов

Все тесты

```bash
uv run pytest tests/
```

Конкретный модуль

```bash
uv run pytest tests/test_models.py
```

С остановкой на первой ошибке

```bash
uv run pytest tests/ -x
```

С кратким выводом

```bash
uv run pytest tests/ --tb=short
```

### Структура проекта

```
firefeed/
├── api/                 # FastAPI приложение
├── tests/                 # Unit-тесты
├── scripts/              # Скрипты автоматизации
├── doc/                  # Полная документация
├── bot.py              # Telegram бот
├── rss_parser.py       # RSS парсер
├── firefeed_translator.py    # Переводчик
├── firefeed_dublicate_detector.py  # Детектор дубликатов
├── user_manager.py     # Менеджер пользователей
├── requirements.txt    # Зависимости
└── config/            # Конфигурации
```

### Workflow проверки качества кода

Проект использует современные инструменты качества кода от Meta для автоматизации рефакторинга и поддержания высокого стандарта кода.

#### Быстрый старт - полная проверка:

```bash
# Все проверки одним скриптом
./scripts/test_meta_tools.sh
```

#### Пошаговая проверка:

```bash
# 1. Сортировка импортов
uv run usort .

# 2. Проверка типов
uv run pyrefly check

# 3. Проверка стиля кода
uv run ruff check .

# 4. Запуск тестов
uv run pytest
```

#### Автоматические исправления:

```bash
# Применить все безопасные codemods
python scripts/apply_codemods.py

# Исправить стиль кода
uv run ruff check --fix .

# Трансформации libcst
python scripts/libcst_transformations.py проблемный_файл.py
```

#### Инструменты качества:

| Инструмент | Версия | Назначение |
|------------|--------|------------|
| usort | 1.1.0 | Сортировка импортов |
| pyrefly | 0.41.2 | Проверка типов |
| libcst | 1.8.6 | Трансформации кода |
| codemod | 1.0.0 | Автоматические рефакторинги |

**📖 Полная документация**: См. папку [`doc/`](doc/) для подробных руководств:
- [`doc/META_TOOLS_INTEGRATION_GUIDE.md`](doc/META_TOOLS_INTEGRATION_GUIDE.md) - Полное руководство
- [`doc/META_TOOLS_QUICK_REFERENCE.md`](doc/META_TOOLS_QUICK_REFERENCE.md) - Краткий справочник

## Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.