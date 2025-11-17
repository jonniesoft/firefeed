#!/bin/bash

# Переходим в каталог проекта для корректной работы UV
cd /root/firefeed

# Запускаем Telegram бота через UV с зафиксированными зависимостями
# UV использует .python-version (3.13) и uv.lock для детерминированного окружения
# Флаг --no-sync пропускает проверку синхронизации (окружение уже синхронизировано при деплое)
# Флаг --frozen гарантирует, что uv.lock не будет изменён
uv run --no-sync --frozen python /var/www/firefeed/data/integrations/telegram/bot.py
