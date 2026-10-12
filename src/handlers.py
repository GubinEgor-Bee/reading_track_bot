"""Обработчики команд Telegram-бота."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start."""
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, {user}! Я бот для чтения.\n"
        "Я помогу тебе отслеживать прочитанное и находить новые книги.\n"
        "Используй /help, чтобы узнать список команд."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /help."""
    await update.message.reply_text(
        "📚 Мои команды:\n"
        "/track - Отметить прочитанные страницы\n"
        "/recommend - Получить рекомендацию книги\n"
        "/stats - Посмотреть статистику\n"
    )


async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /recommend (заглушка)."""
    await update.message.reply_text(
        "📖 Рекомендация на сегодня:\n"
        "«Программист-прагматик» (Дэвид Томас, Эндрю Хант) — "
        "отличная книга для развития архитектурного мышления!"
    )


async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /track (заглушка)."""
    await update.message.reply_text(
        "📝 Функция добавления прочитанных страниц в разработке!"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /stats (заглушка)."""
    await update.message.reply_text(
        "📊 Твоя статистика:\nПрочитано книг: 0\nПрочитано страниц: 0"
    )
