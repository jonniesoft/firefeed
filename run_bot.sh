#!/bin/bash

# Запускаем Telegram бота через UV с зафиксированными зависимостями
# UV использует .python-version (3.13) и uv.lock для детерминированного окружения
uv run --frozen python /var/www/firefeed/data/integrations/telegram/bot.py
