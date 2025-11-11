from aiosmtplib import send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timezone
from config import SMTP_CONFIG

# Настройка логирования
logger = logging.getLogger("email_service.sender")
logger.setLevel(logging.INFO)


class EmailSender:
    def __init__(self):
        self.smtp_config = SMTP_CONFIG
        self.sender_email = self.smtp_config["email"]

        # Настройка Jinja2 для загрузки шаблонов
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    async def send_password_reset_email(self, to_email: str, reset_token: str, language: str = "en") -> bool:
        """
        Отправляет email с ссылкой для сброса пароля

        Args:
            to_email (str): Email получателя
            reset_token (str): Токен сброса пароля
            language (str): Язык письма ('en', 'ru', 'de')

        Returns:
            bool: True если письмо отправлено успешно, False в случае ошибки
        """
        start_ts = datetime.now(timezone.utc)
        logger.info(f"[EmailSender] Password reset email start: to={to_email} at {start_ts.isoformat()}Z")
        try:
            # Создаем сообщение
            message = MIMEMultipart("alternative")
            message["Subject"] = self._get_reset_subject(language)
            message["From"] = self.sender_email
            message["To"] = to_email

            # Получаем содержимое письма из шаблонов
            text_content = self._get_reset_text_content(reset_token, language)
            html_content = self._render_reset_html_template(reset_token, language)

            # Создаем части письма
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")

            # Добавляем части в сообщение
            message.attach(text_part)
            message.attach(html_part)

            # Отправляем email асинхронно с таймаутами (connect/read/write по 10 секунд)
            # Для порта 465 используем SSL, для других портов - TLS
            use_ssl = self.smtp_config["port"] == 465
            use_start_tls = self.smtp_config.get("use_tls", False) and not use_ssl

            await send(
                message,
                hostname=self.smtp_config["server"],
                port=self.smtp_config["port"],
                username=self.sender_email,
                password=self.smtp_config["password"],
                start_tls=use_start_tls,
                use_tls=use_ssl,
                timeout=10,
            )

            duration = (datetime.now(timezone.utc) - start_ts).total_seconds()
            if duration > 10:
                logger.warning(f"[EmailSender] Password reset email slow ({duration:.3f}s) to {to_email}")
            else:
                logger.info(f"[EmailSender] Password reset email sent in {duration:.3f}s to {to_email}")
            return True

        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_ts).total_seconds()
            logger.error(f"[EmailSender] Failed to send password reset email to {to_email} after {duration:.3f}s: {str(e)}")
            return False

    async def send_verification_email(self, to_email: str, verification_code: str, language: str = "en") -> bool:
        """
        Отправляет email с кодом подтверждения регистрации

        Args:
            to_email (str): Email получателя
            verification_code (str): Код подтверждения
            language (str): Язык письма ('en', 'ru', 'de')

        Returns:
            bool: True если письмо отправлено успешно, False в случае ошибки
        """
        start_ts = datetime.now(timezone.utc)
        logger.info(f"[EmailSender] Verification email start: to={to_email} at {start_ts.isoformat()}Z")
        try:
            # Создаем сообщение
            message = MIMEMultipart("alternative")
            message["Subject"] = self._get_subject(language)
            message["From"] = self.sender_email
            message["To"] = to_email

            # Получаем содержимое письма из шаблонов
            text_content = self._get_text_content(verification_code, language)
            html_content = self._render_html_template(verification_code, language)

            # Создаем части письма
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")

            # Добавляем части в сообщение
            message.attach(text_part)
            message.attach(html_part)

            # Отправляем email асинхронно с таймаутом 10 секунд
            # Для порта 465 используем SSL, для других портов - TLS
            use_ssl = self.smtp_config["port"] == 465
            use_start_tls = self.smtp_config.get("use_tls", False) and not use_ssl

            await send(
                message,
                hostname=self.smtp_config["server"],
                port=self.smtp_config["port"],
                username=self.sender_email,
                password=self.smtp_config["password"],
                start_tls=use_start_tls,
                use_tls=use_ssl,
                timeout=10,
            )

            duration = (datetime.now(timezone.utc) - start_ts).total_seconds()
            if duration > 10:
                logger.warning(f"[EmailSender] Verification email slow ({duration:.3f}s) to {to_email}")
            else:
                logger.info(f"[EmailSender] Verification email sent in {duration:.3f}s to {to_email}")
            return True

        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_ts).total_seconds()
            logger.error(f"[EmailSender] Failed to send verification email to {to_email} after {duration:.3f}s: {str(e)}")
            return False

    def _get_reset_subject(self, language: str) -> str:
        """Возвращает тему письма сброса пароля в зависимости от языка"""
        subjects = {
            "en": "FireFeed - Password Reset",
            "ru": "FireFeed - Сброс пароля",
            "de": "FireFeed - Passwort zurücksetzen",
        }
        return subjects.get(language, subjects["en"])

    def _get_subject(self, language: str) -> str:
        """Возвращает тему письма в зависимости от языка"""
        subjects = {
            "en": "FireFeed - Account Verification Code",
            "ru": "FireFeed - Код подтверждения аккаунта",
            "de": "FireFeed - Konto-Verifizierungscode",
        }
        return subjects.get(language, subjects["en"])

    def _get_reset_text_content(self, reset_token: str, language: str) -> str:
        """Возвращает текстовую версию письма сброса пароля"""
        reset_link = f"https://firefeed.net/api/v1/auth/reset-password/confirm?token={reset_token}"
        if language == "ru":
            return f"""
FireFeed - Сброс пароля

Вы запросили сброс пароля для вашего аккаунта FireFeed.

Для сброса пароля перейдите по следующей ссылке:
{reset_link}

Эта ссылка действительна в течение 1 часа.

Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.

С уважением,
Команда FireFeed
            """.strip()
        elif language == "de":
            return f"""
FireFeed - Passwort zurücksetzen

Sie haben eine Passwort-Zurücksetzung für Ihr FireFeed-Konto angefordert.

Um Ihr Passwort zurückzusetzen, klicken Sie auf den folgenden Link:
{reset_link}

Dieser Link ist 1 Stunde gültig.

Wenn Sie keine Passwort-Zurücksetzung angefordert haben, ignorieren Sie diese E-Mail bitte.

Mit freundlichen Grüßen,
FireFeed Team
            """.strip()
        else:
            return f"""
FireFeed - Password Reset

You have requested a password reset for your FireFeed account.

To reset your password, click the following link:
{reset_link}

This link is valid for 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
FireFeed Team
            """.strip()

    def _get_text_content(self, verification_code: str, language: str) -> str:
        """Возвращает текстовую версию письма"""
        if language == "ru":
            return f"""
Добро пожаловать в FireFeed!

Ваш код подтверждения регистрации: {verification_code}

Пожалуйста, введите этот код на странице регистрации для завершения процесса.

С уважением,
Команда FireFeed
            """.strip()
        elif language == "de":
            return f"""
Willkommen bei FireFeed!

Ihr Konto-Verifizierungscode lautet: {verification_code}

Bitte geben Sie diesen Code auf der Registrierungsseite ein, um den Vorgang abzuschließen.

Mit freundlichen Grüßen,
FireFeed Team
            """.strip()
        else:
            return f"""
Welcome to FireFeed!

Your account verification code is: {verification_code}

Please enter this code on the registration page to complete the process.

Best regards,
FireFeed Team
            """.strip()

    def _render_reset_html_template(self, reset_token: str, language: str) -> str:
        """Рендерит HTML шаблон сброса пароля с помощью Jinja2"""
        # Определяем имя файла шаблона
        template_files = {
            "en": "password_reset_email_en.html",
            "ru": "password_reset_email_ru.html",
            "de": "password_reset_email_de.html",
        }

        template_name = template_files.get(language, template_files["en"])

        try:
            # Загружаем и рендерим шаблон
            template = self.jinja_env.get_template(template_name)
            return template.render(reset_token=reset_token, current_year=datetime.now(timezone.utc).year)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            # Возвращаем базовый HTML контент если шаблон не найден
            return self._get_fallback_reset_html_content(reset_token, language)

    def _render_html_template(self, verification_code: str, language: str) -> str:
        """Рендерит HTML шаблон с помощью Jinja2"""
        # Определяем имя файла шаблона
        template_files = {
            "en": "verification_email_en.html",
            "ru": "verification_email_ru.html",
            "de": "verification_email_de.html",
        }

        template_name = template_files.get(language, template_files["en"])

        try:
            # Загружаем и рендерим шаблон
            template = self.jinja_env.get_template(template_name)
            return template.render(verification_code=verification_code, current_year=datetime.now(timezone.utc).year)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            # Возвращаем базовый HTML контент если шаблон не найден
            return self._get_fallback_html_content(verification_code, language)

    def _get_fallback_html_content(self, verification_code: str, language: str) -> str:
        """Возвращает базовый HTML контент если шаблон не найден"""
        year = datetime.now(timezone.utc).year
        if language == "ru":
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FireFeed - Подтверждение регистрации</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35;">🔥 FireFeed</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 10px; border-left: 4px solid #ff6b35;">
            <h2 style="color: #333; margin-top: 0;">Добро пожаловать в FireFeed!</h2>
            
            <p>Спасибо за регистрацию в нашем сервисе новостей.</p>
            
            <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #666;">Ваш код подтверждения:</p>
                <h3 style="margin: 10px 0; font-size: 32px; color: #ff6b35; letter-spacing: 3px;">{verification_code}</h3>
                <p style="margin: 0; font-size: 14px; color: #999;">Введите этот код на странице регистрации</p>
            </div>
            
            <p>Если вы не регистрировались в FireFeed, просто проигнорируйте это письмо.</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            <p>© {year} FireFeed. Все права защищены.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
        elif language == "de":
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FireFeed - Konto-Verifizierung</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35;">🔥 FireFeed</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 10px; border-left: 4px solid #ff6b35;">
            <h2 style="color: #333; margin-top: 0;">Willkommen bei FireFeed!</h2>
            
            <p>Vielen Dank für Ihre Registrierung bei unserem Nachrichtendienst.</p>
            
            <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #666;">Ihr Verifizierungscode:</p>
                <h3 style="margin: 10px 0; font-size: 32px; color: #ff6b35; letter-spacing: 3px;">{verification_code}</h3>
                <p style="margin: 0; font-size: 14px; color: #999;">Geben Sie diesen Code auf der Registrierungsseite ein</p>
            </div>
            
            <p>Wenn Sie sich nicht bei FireFeed registriert haben, ignorieren Sie bitte diese E-Mail.</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            <p>© {year} FireFeed. Alle Rechte vorbehalten.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
        else:
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FireFeed - Account Verification</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35;">🔥 FireFeed</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 10px; border-left: 4px solid #ff6b35;">
            <h2 style="color: #333; margin-top: 0;">Welcome to FireFeed!</h2>
            
            <p>Thank you for registering with our news service.</p>
            
            <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #666;">Your verification code:</p>
                <h3 style="margin: 10px 0; font-size: 32px; color: #ff6b35; letter-spacing: 3px;">{verification_code}</h3>
                <p style="margin: 0; font-size: 14px; color: #999;">Enter this code on the registration page</p>
            </div>
            
            <p>If you didn't register with FireFeed, please ignore this email.</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            <p>© {year} FireFeed. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()

    def _get_fallback_reset_html_content(self, reset_token: str, language: str) -> str:
        """Возвращает базовый HTML контент для сброса пароля если шаблон не найден"""
        year = datetime.now(timezone.utc).year
        reset_link = f"https://firefeed.net/api/v1/auth/reset-password/confirm?token={reset_token}"
        if language == "ru":
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FireFeed - Сброс пароля</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35;">🔥 FireFeed</h1>
        </div>

        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 10px; border-left: 4px solid #ff6b35;">
            <h2 style="color: #333; margin-top: 0;">Сброс пароля</h2>

            <p>Вы запросили сброс пароля для вашего аккаунта FireFeed.</p>

            <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #666;">Для сброса пароля нажмите на кнопку:</p>
                <a href="{reset_link}" style="display: inline-block; background-color: #ff6b35; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; font-weight: bold;">Сбросить пароль</a>
                <p style="margin: 10px 0; font-size: 14px; color: #999;">Ссылка действительна 1 час</p>
            </div>

            <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
        </div>

        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            <p>© {year} FireFeed. Все права защищены.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
        elif language == "de":
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FireFeed - Passwort zurücksetzen</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35;">🔥 FireFeed</h1>
        </div>

        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 10px; border-left: 4px solid #ff6b35;">
            <h2 style="color: #333; margin-top: 0;">Passwort zurücksetzen</h2>

            <p>Sie haben eine Passwort-Zurücksetzung für Ihr FireFeed-Konto angefordert.</p>

            <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #666;">Klicken Sie auf die Schaltfläche, um Ihr Passwort zurückzusetzen:</p>
                <a href="{reset_link}" style="display: inline-block; background-color: #ff6b35; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; font-weight: bold;">Passwort zurücksetzen</a>
                <p style="margin: 10px 0; font-size: 14px; color: #999;">Link ist 1 Stunde gültig</p>
            </div>

            <p>Wenn Sie keine Passwort-Zurücksetzung angefordert haben, ignorieren Sie bitte diese E-Mail.</p>
        </div>

        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            <p>© {year} FireFeed. Alle Rechte vorbehalten.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
        else:
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FireFeed - Password Reset</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35;">🔥 FireFeed</h1>
        </div>

        <div style="background-color: #f9f9f9; padding: 30px; border-radius: 10px; border-left: 4px solid #ff6b35;">
            <h2 style="color: #333; margin-top: 0;">Password Reset</h2>

            <p>You have requested a password reset for your FireFeed account.</p>

            <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #666;">Click the button below to reset your password:</p>
                <a href="{reset_link}" style="display: inline-block; background-color: #ff6b35; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; font-weight: bold;">Reset Password</a>
                <p style="margin: 10px 0; font-size: 14px; color: #999;">Link is valid for 1 hour</p>
            </div>

            <p>If you did not request a password reset, please ignore this email.</p>
        </div>

        <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
            <p>© {year} FireFeed. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()


# Создаем глобальный экземпляр отправщика
email_sender = EmailSender()


# Удобная функция для отправки письма
async def send_verification_email(to_email: str, verification_code: str, language: str = "en") -> bool:
    """
    Удобная функция для отправки email с кодом подтверждения

    Args:
        to_email (str): Email получателя
        verification_code (str): Код подтверждения
        language (str): Язык письма ('en', 'ru', 'de')

    Returns:
        bool: True если письмо отправлено успешно, False в случае ошибки
    """
    return await email_sender.send_verification_email(to_email, verification_code, language)


async def send_password_reset_email(to_email: str, reset_token: str, language: str = "en") -> bool:
    """
    Удобная функция для отправки email с ссылкой сброса пароля

    Args:
        to_email (str): Email получателя
        reset_token (str): Токен сброса пароля
        language (str): Язык письма ('en', 'ru', 'de')

    Returns:
        bool: True если письмо отправлено успешно, False в случае ошибки
    """
    return await email_sender.send_password_reset_email(to_email, reset_token, language)
