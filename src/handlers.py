"""Обработчики команд и диалогов Telegram-бота."""

import random
import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from src.models import RECOMMENDATIONS, QUOTES

logger = logging.getLogger(__name__)

# Этапы (состояния) для диалогов
TRACK_TITLE, TRACK_PAGES = range(2)
REV_TITLE, REV_TEXT = range(2)


# --- 1. Базовые команды ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, {user}! Я твой бот-ассистент для чтения 📚\n\n"
        "Доступные команды:\n"
        "/track - Добавить прочитанные страницы\n"
        "/review - Написать рецензию на книгу\n"
        "/stats - Посмотреть статистику\n"
        "/recommend - Получить рекомендацию\n"
        "/subscribe - Подписаться на отрывки и напоминания\n"
        "/cancel - Отменить ввод данных"
    )


# --- 2. Рекомендации книг ---
async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    book = random.choice(RECOMMENDATIONS)
    await update.message.reply_text(
        f"📚 Рекомендую почитать:\n\n*{book}*", parse_mode="Markdown"
    )


# --- 3. Ежедневные отрывки и Напоминания (JobQueue) ---
async def send_quote_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    quote = random.choice(QUOTES)
    await context.bot.send_message(
        chat_id=job.chat_id, text=f"🌟 *Отрывок дня:*\n\n{quote}", parse_mode="Markdown"
    )


async def send_reminder_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="⏰ *Напоминание:* Время почитать! Уделите книге хотя бы 15 минут, а потом отметьте прогресс командой /track.",
        parse_mode="Markdown",
    )


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id

    # Удаляем старые задачи, чтобы не дублировать подписку
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    # Запускаем отрывки (каждые 24 часа, первый придет через 10 секунд для проверки)
    context.job_queue.run_repeating(
        send_quote_job, interval=86400, first=10, chat_id=chat_id, name=str(chat_id)
    )
    # Запускаем напоминания (каждые 24 часа, первое через 12 часов)
    context.job_queue.run_repeating(
        send_reminder_job,
        interval=86400,
        first=15,
        chat_id=chat_id,
        name=f"{chat_id}_reminder",
    )

    await update.message.reply_text(
        "✅ Вы успешно подписались на ежедневные отрывки и напоминания! (Первый отрывок придет через 10 секунд)."
    )


# --- 4. Отслеживание прочитанного ---
async def track_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Какую книгу вы сейчас читаете? (Введите название)")
    return TRACK_TITLE


async def track_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["temp_title"] = update.message.text
    await update.message.reply_text(
        "Сколько страниц вы прочитали сегодня? (Введите число)"
    )
    return TRACK_PAGES


async def track_pages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pages = update.message.text
    if not pages.isdigit():
        await update.message.reply_text("Пожалуйста, введите число.")
        return TRACK_PAGES

    title = context.user_data.get("temp_title")

    # Инициализируем хранилище пользователя, если его еще нет
    if "books" not in context.user_data:
        context.user_data["books"] = {}
    if title not in context.user_data["books"]:
        context.user_data["books"][title] = {"pages": 0, "review": None}

    context.user_data["books"][title]["pages"] += int(pages)
    total_pages = context.user_data["books"][title]["pages"]

    await update.message.reply_text(
        f"✅ Прогресс сохранен!\n📖 Книга: {title}\nВсего прочитано: {total_pages} стр."
    )
    return ConversationHandler.END


# --- 5. Обзоры и рецензии ---
async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "На какую книгу вы хотите написать отзыв? (Введите название)"
    )
    return REV_TITLE


async def review_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["temp_rev_title"] = update.message.text
    await update.message.reply_text("Напишите вашу рецензию:")
    return REV_TEXT


async def review_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    title = context.user_data.get("temp_rev_title")
    review = update.message.text

    if "books" not in context.user_data:
        context.user_data["books"] = {}
    if title not in context.user_data["books"]:
        context.user_data["books"][title] = {"pages": 0, "review": None}

    context.user_data["books"][title]["review"] = review
    await update.message.reply_text(f"✅ Отзыв на книгу «{title}» успешно сохранен!")
    return ConversationHandler.END


# --- 6. Статистика (Общая информация) ---
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    books = context.user_data.get("books", {})
    if not books:
        await update.message.reply_text(
            "Вы еще не добавили ни одной книги. Используйте /track."
        )
        return

    msg = "📊 *Ваша статистика чтения:*\n\n"
    for title, data in books.items():
        msg += f"📖 *{title}*\n"
        msg += f"   Прочитано: {data['pages']} стр.\n"
        if data["review"]:
            msg += f"   Отзыв: _{data['review']}_\n"
        msg += "\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# --- Отмена диалогов ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


# --- Сборка диалогов (для main.py) ---
def get_track_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("track", track_start)],
        states={
            TRACK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, track_title)],
            TRACK_PAGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, track_pages)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


def get_review_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("review", review_start)],
        states={
            REV_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_title)],
            REV_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
