# syntax=docker/dockerfile:1.7-labs

# Multi-stage build для оптимизации размера образа

# Builder stage - установка зависимостей
FROM python:3.14-slim AS builder

# Копируем UV из официального образа (версия зафиксирована для воспроизводимости)
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Устанавливаем переменные окружения для оптимизации UV
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_INSTALLER_METADATA=1

# Устанавливаем системные зависимости для компиляции ML-библиотек
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта для установки зависимостей
# Используем * для условного копирования (не упадет, если файлов нет)
COPY pyproject.toml* uv.lock* requirements.txt ./

# Устанавливаем зависимости с использованием cache mount для ускорения
# Если есть pyproject.toml - используем uv sync, иначе - pip install из requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f pyproject.toml ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv pip install --system -r requirements.txt; \
    fi

# Копируем весь код проекта
COPY . .

# Финальная синхронизация для production-ready установки
# Если используется pyproject.toml - финальная синхронизация, иначе - пропускаем
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f pyproject.toml ]; then \
        uv sync --frozen --no-editable; \
    fi

# Runtime stage - минимальный образ для запуска
FROM python:3.14-slim

# Устанавливаем runtime-зависимости для ML-библиотек
# libgomp1 - для OpenMP (используется torch, scikit-learn)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код приложения и виртуальное окружение из builder stage
COPY --from=builder /app /app

# Добавляем .venv/bin в PATH
ENV PATH="/app/.venv/bin:$PATH"

# Создаем директорию для данных (если нужно для изображений, но лучше монтировать volume)
RUN mkdir -p /app/data

# Экспортируем порт для API (uvicorn по умолчанию 8000)
EXPOSE 8000

# По умолчанию запускаем API через uvicorn
# Для запуска бота или парсера можно переопределить CMD при запуске контейнера
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
