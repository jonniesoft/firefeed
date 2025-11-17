# Настройка Gmail для FireFeed

Данный файл содержит инструкции по настройке Gmail для отправки email в FireFeed.

## Настройка Gmail

### 1. Включение 2FA

Для использования паролей приложений необходимо включить двухфакторную аутентификацию:
1. Перейдите в [Google Account Security](https://myaccount.google.com/security)
2. В разделе "Вход в Google" включите 2FA

### 2. Создание пароля приложения

1. Перейдите в [Google Account Security](https://myaccount.google.com/apppasswords)
2. Выберите "Mail" и "Other (Custom name)"
3. Введите название: `FireFeed App`
4. Нажмите "Generate"
5. **Скопируйте сгенерированный пароль** (16 символов, без пробелов)
6. **ВАЖНО**: Сохраните пароль в безопасном месте!

⚠️ **Внимание**: Пароль приложения отображается только один раз!

### 3. Настройка .env

Отредактируйте файл `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-gmail@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_USE_TLS=True
```

### 4. Тестирование

После настройки можно протестировать отправку email:

```bash
# Запуск в контейнере
docker-compose up -d

# Проверка логов
docker-compose logs -f firefeed-api
```

## Troubleshooting

### Ошибка: "Less secure app access"

**Решение**: Используйте пароль приложения вместо основного пароля Gmail.

### Ошибка: "Username and Password not accepted"

**Возможные причины**:
1. Неправильный пароль приложения
2. 2FA не включен
3. Пароль приложения уже был использован ранее

**Решение**:
1. Проверьте, что 2FA включен
2. Создайте новый пароль приложения
3. Обновите `.env` файл

### Ошибка: "Connection timeout"

**Возможные причины**:
1. Блокировка порта 587 брандмауэром
2. Проблемы с интернет-соединением

**Решение**:
1. Проверьте подключение к интернету
2. Попробуйте порт 465 (SSL):
   ```env
   SMTP_PORT=465
   SMTP_USE_TLS=False
   ```

### Не приходят письма

**Возможные причины**:
1. Письма попадают в спам
2. Неправильный email получателя
3. Ошибки в коде отправки

**Решение**:
1. Проверьте папку "Спам" у получателя
2. Проверьте логи: `docker-compose logs firefeed-api`
3. Убедитесь, что email валидный

## Безопасность

### ⚠️ Важные предупреждения:

1. **Никогда не используйте основной пароль Gmail** в `.env` файле
2. **Всегда используйте пароли приложений** для сторонних приложений
3. **Пароль приложения дает полный доступ** к отправке email от вашего имени
4. **Если пароль скомпрометирован**, немедленно отзовите его в настройках Google

### Защита .env файла:

```bash
# Установите правильные права доступа
chmod 600 .env

# Добавьте в .gitignore (уже сделано)
echo ".env" >> .gitignore
```

## Альтернативы Gmail

Если Gmail не подходит, можно использовать:

1. **SendGrid** (рекомендуется для продакшена)
   - SMTP: `smtp.sendgrid.net`
   - Порт: `587`
   - API Key в пароле

2. **Mailgun**
   - SMTP: `smtp.mailgun.org`
   - Порт: `587` или `465`

3. **AWS SES**
   - Требует настройки AWS credentials
   - Более сложная интеграция

## Дополнительные ресурсы

- [Google App Passwords Help](https://support.google.com/mail/answer/185833)
- [Google Account Security](https://myaccount.google.com/security)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
