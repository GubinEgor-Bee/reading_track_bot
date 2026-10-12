"""Главный модуль запуска бота."""

import logging
from telegram.ext import Application, CommandHandler
import config
from src import handlers

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> None:
    """Запуск приложения."""
    if not config.BOT_TOKEN:
        logger.error("Токен не найден! Добавьте его в config.py.")
        return

    # Создание приложения
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("recommend", handlers.recommend_command))
    application.add_handler(CommandHandler("track", handlers.track_command))
    application.add_handler(CommandHandler("stats", handlers.stats_command))

    # Запуск бота
    logger.info("Бот успешно запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
