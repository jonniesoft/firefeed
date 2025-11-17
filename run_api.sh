#!/bin/bash

# Запускаем FastAPI через uvicorn с зафиксированными зависимостями
# UV использует .python-version (3.13) и uv.lock для детерминированного окружения
uv run --frozen uvicorn api.main:app --host 127.0.0.1 --port 8000
