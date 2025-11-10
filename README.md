# FireFeed - AI-powered RSS aggregator and parser

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](https://github.com/yuremweiland/firefeed/actions)

Современный новостной агрегатор с поддержкой искусственного интеллекта для автоматического сбора, обработки и распространения новостей на нескольких языках.

**Официальный сайт**: https://firefeed.net

## Содержание

- [Обзор проекта](#обзор-проекта)
- [Основные возможности](#основные-возможности)
- [Технический стек](#технический-стек)
- [Архитектура](#архитектура)
- [Установка и запуск](#установка-и-запуск)
- [Конфигурация](#конфигурация)
- [API документация](#api-документация)
- [Разработка](#разработка)
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
- Docker-контейнеризация
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
- UV package manager (установка: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
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

**Примечание**: После добавления `pyproject.toml` и `uv.lock` используйте `uv sync` вместо `uv pip install`. До тех пор используется `requirements.txt` для установки зависимостей.

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

# Запуск бота
./run_bot.sh

# Запуск API
./run_api.sh
```

### Запуск через Docker

Проект поддерживает Docker-контейнеризацию с использованием multi-stage сборки для оптимизации размера образа.

**Требования:**
- Docker 20.10+ с поддержкой BuildKit

**Сборка образа:**

```bash
# Включите BuildKit (рекомендуется)
export DOCKER_BUILDKIT=1

# Соберите образ
docker build -t firefeed:latest .
```

**Примечание**: Dockerfile использует BuildKit-специфичные функции (cache mounts). Убедитесь, что BuildKit включен через переменную окружения `DOCKER_BUILDKIT=1` или настройте Docker daemon для использования BuildKit по умолчанию.

**Запуск контейнера:**

```bash
# Запуск API
docker run -d -p 8000:8000 --env-file .env firefeed:latest

# Запуск бота (переопределение CMD)
docker run -d --env-file .env firefeed:latest python bot.py

# Запуск RSS парсера
docker run -d --env-file .env firefeed:latest python rss_parser.py
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

**Примечание**: `pyproject.toml` и `uv.lock` будут созданы в следующей фазе миграции. После их добавления используйте `uv sync` вместо `uv pip install -r requirements.txt`.

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
pytest tests/
```

Конкретный модуль

```bash
pytest tests/test_models.py
```

С остановкой на первой ошибке

```bash
pytest tests/ -x
```

С кратким выводом

```bash
pytest tests/ --tb=short
```

### Структура проекта

```
firefeed/
├── api/                 # FastAPI приложение
├── tests/                 # Unit-тесты
├── bot.py              # Telegram бот
├── rss_parser.py       # RSS парсер
├── firefeed_translator.py    # Переводчик
├── firefeed_dublicate_detector.py  # Детектор дубликатов
├── user_manager.py     # Менеджер пользователей
├── requirements.txt    # Зависимости
└── config/            # Конфигурации
```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.