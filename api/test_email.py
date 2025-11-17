import asyncio
import logging
import sys
import traceback
from pathlib import Path

# Добавляем корень проекта в путь поиска модулей
sys.path.append(str(Path(__file__).resolve().parent.parent))

from api.email_service.sender import send_verification_email

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_email():
    # Замени на свой email для тестирования
    test_email = "jonnie.software.ai@gmail.com"  # <-- Замени на реальный email
    verification_code = "123456"

    logger.info(f"Отправляем тестовое письмо на {test_email}")
    logger.info(f"Код подтверждения: {verification_code}")

    # Тестируем отправку на разных языках
    for language in ["en", "ru", "de"]:
        logger.info(f"Тестируем отправку на языке: {language}")
        try:
            success = await send_verification_email(test_email, verification_code, language)
            if success:
                logger.info(f"✅ Письмо на {language} успешно отправлено!")
            else:
                logger.error(f"❌ Ошибка при отправке письма на {language}")
        except Exception as e:
            logger.error(f"❌ Исключение при отправке письма на {language}: {e}")
            logger.error(f"Полный traceback: {traceback.format_exc()}")

    logger.info("Тест завершен!")


if __name__ == "__main__":
    asyncio.run(test_email())
