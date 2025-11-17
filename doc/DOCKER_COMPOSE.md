# Docker Compose для FireFeed

Данное руководство описывает, как запускать FireFeed в контейнерах с помощью Docker Compose.

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)
- [Запуск сервисов](#запуск-сервисов)
- [Разработка](#разработка)
- [Мониторинг](#мониторинг)
- [Остановка](#остановка)
- [Устранение неполадок](#устранение-неполадок)

## Быстрый старт

### 1. Настройка переменных окружения

```bash
# Скопируйте файл примера
cp .env.example .env

# Отредактируйте .env и заполните реальными значениями
nano .env
```

**Минимальные настройки для запуска:**
- `DB_PASSWORD` - сложный пароль для PostgreSQL
- `JWT_SECRET_KEY` - сгенерируйте: `openssl rand -hex 32`
- `BOT_TOKEN` - токен от @BotFather (для работы бота)
- `SMTP_*` - настройки почты (для верификации email)

### 2. Запуск всех сервисов

```bash
# Поднять все сервисы в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### 3. Проверка состояния

```bash
# Статус всех сервисов
docker-compose ps

# Логи конкретного сервиса
docker-compose logs -f firefeed-api
```

## Конфигурация

### Основные сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| `db` | 5432 | PostgreSQL 16 + pgvector |
| `firefeed-api` | 8000 | FastAPI приложение |
| `firefeed-bot` | - | Telegram бот |
| `firefeed-parser` | - | RSS парсер |
| `redis` | 6379 | Кэш и очереди |

### Переменные окружения

Все переменные берутся из `.env` файла. Основные:

```bash
# База данных
DB_HOST=db
DB_USER=firefeed_user
DB_PASSWORD=your_password
DB_NAME=firefeed
DB_PORT=5432

# Приложение
JWT_SECRET_KEY=your_jwt_secret
BOT_TOKEN=your_bot_token
WEBHOOK_URL=http://localhost:5000/webhook

# Почта
SMTP_SERVER=smtp.example.com
SMTP_EMAIL=noreply@example.com
SMTP_PASSWORD=your_smtp_password
```

## Запуск сервисов

### Полный стек

```bash
# Запуск всех сервисов
docker-compose up -d

# С зависимостями (правильный порядок)
docker-compose up -d db
sleep 10  # Ждем инициализации БД
docker-compose up -d
```

### Отдельные сервисы

```bash
# Только БД
docker-compose up -d db

# БД + API
docker-compose up -d db firefeed-api

# Все кроме бота (для API тестирования)
docker-compose up -d db redis firefeed-api firefeed-parser
```

### Обновление образов

```bash
# Пересборка образов
docker-compose build

# Запуск с пересборкой
docker-compose up -d --build
```

## Разработка

### Режим разработки

Для разработки используйте `docker-compose.override.yml`:

```bash
# Автоматически загружается docker-compose
docker-compose up -d
```

**Особенности override:**
- Горячая перезагрузка кода
- DEBUG логирование
- Порт 5678 для отладки
- PgAdmin4 на http://localhost:5050
- Volume mounts для live-редактирования

### PgAdmin (только в разработке)

```bash
# Веб-интерфейс: http://localhost:5050
# Email: admin@firefeed.local
# Password: admin

# Подключение к БД:
# Host: db
# Port: 5432
# Database: firefeed
# Username: из .env (DB_USER)
# Password: из .env (DB_PASSWORD)
```

### Live-редактирование

```bash
# Отредактируйте код на хосте
# Изменения автоматически применяются (thanks to volumes)
```

### Отладка

```bash
# Подключение к контейнеру
docker-compose exec firefeed-api bash

# Отладка Python с pdb
# В коде добавьте: import pdb; pdb.set_trace()
# Подключитесь к контейнеру на порт 5678
```

## Мониторинг

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f firefeed-api

# Последние N строк
docker-compose logs --tail=100 firefeed-db

# Логи с временными метками
docker-compose logs -f -t firefeed-bot
```

### Проверка состояния

```bash
# Статус сервисов
docker-compose ps

# Статистика использования ресурсов
docker stats

# Подробная информация о контейнере
docker-compose exec firefeed-api cat /etc/hostname
```

### Health checks

```bash
# Проверка health check БД
docker-compose exec db pg_isready -U firefeed_user -d firefeed

# Проверка доступности API
curl http://localhost:8000/health
```

## Остановка

### Остановка сервисов

```bash
# Остановка без удаления
docker-compose stop

# Остановка и удаление контейнеров
docker-compose down

# Полная очистка (включая volumes)
docker-compose down -v
```

### Очистка

```bash
# Удаление всех данных БД (ВНИМАНИЕ!)
docker-compose down -v
docker volume rm firefeed_postgres_data

# Пересоздание БД с нуля
docker-compose down -v
docker-compose up -d db
```

## Устранение неполадок

### БД не запускается

```bash
# Проверка логов
docker-compose logs db

# Частая проблема: неправильные credentials в .env
# Убедитесь что DB_USER и DB_PASSWORD корректны
```

### Ошибка подключения к БД

```bash
# Проверка что БД готова
docker-compose exec db pg_isready -U ${DB_USER:-firefeed_user} -d ${DB_NAME:-firefeed}

# Проверка переменных окружения
docker-compose exec firefeed-api env | grep DB_
```

### Сервисы не общаются между собой

```bash
# Проверка общей сети
docker network ls
docker network inspect firefeed_firefeed-network

# Проверка DNS
docker-compose exec firefeed-api ping db
docker-compose exec firefeed-api nc -zv db 5432
```

### Ошибки миграций/инициализации

```bash
# Просмотр логов инициализации
docker-compose logs db

# Ручное подключение к БД
docker-compose exec db psql -U firefeed_user -d firefeed

# Проверка расширений
docker-compose exec db psql -U firefeed_user -d firefeed -c "\dx"
```

### Проблемы с правами доступа

```bash
# Создание директории для данных
mkdir -p ./data
chmod 755 ./data

# Перезапуск с новыми правами
docker-compose up -d
```

### Очистка кэша Docker

```bash
# Очистка неиспользуемых образов
docker system prune -a

# Очистка только volumes (ОСТОРОЖНО!)
docker volume prune
```

### Пересоздание с нуля

```bash
# Полная очистка
docker-compose down -v
docker system prune -af

# Пересборка и запуск
docker-compose build --no-cache
docker-compose up -d
```

## Производительность

### Масштабирование

```bash
# Масштабирование парсеров
docker-compose up -d --scale firefeed-parser=3

# Масштабирование API
docker-compose up -d --scale firefeed-api=2
```

### Ограничение ресурсов

В `docker-compose.yml` можно добавить:

```yaml
services:
  firefeed-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Безопасность

### Запуск от непривилегированного пользователя

В `Dockerfile` добавьте:

```dockerfile
RUN groupadd -r firefeed && useradd -r -g firefeed firefeed
USER firefeed
```

### Секреты

Для продакшена используйте Docker Secrets:

```yaml
services:
  db:
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./db_password.txt
```

## Дополнительные команды

```bash
# Выполнение команд внутри контейнера
docker-compose exec firefeed-api bash
docker-compose exec firefeed-api python -m pytest tests/

# Копирование файлов
docker cp ./local_file.txt firefeed-container:/app/
docker cp firefeed-container:/app/remote_file.txt ./

# Мониторинг в реальном времени
watch -n 1 'docker-compose ps'
```
