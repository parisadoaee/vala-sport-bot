from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = "https://vala-sport-bot.onrender.com" + WEBHOOK_PATH

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

# لینک‌های PDF برنامه‌های مقدماتی
basic_program_links = {
    "برنامه 1": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program1.pdf",
    "برنامه 2": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program2.pdf",
    "برنامه 3": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program3.pdf",
    "برنامه 4": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program4.pdf",
    "برنامه 5": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program5.pdf",
    "برنامه 6": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program6.pdf",
}

# دکمه‌های اصلی
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 مشاوره", callback_data="consult"), InlineKeyboardButton("👛 کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("🏃 حرکات", callback_data="moves"), InlineKeyboardButton("📘 مقدماتی", callback_data="basic")],
        [InlineKeyboardButton("🔰 پایه", callback_data="base"), InlineKeyboardButton("🚀 پیشرفته", callback_data="advanced")],
    ])

# دکمه‌های حرکات
def moves_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖐️ دست", callback_data="move_دست"), InlineKeyboardButton("🦵 پا", callback_data="move_پا")],
        [InlineKeyboardButton("💪 شانه", callback_data="move_شانه"), InlineKeyboardButton("❤️ سینه", callback_data="move_سینه")],
        [InlineKeyboardButton("🏋️‍♂️ شکم", callback_data="move_شکم"), InlineKeyboardButton("🦴 پشت", callback_data="move_پشت")],
        [InlineKeyboardButton("🦶 ساق", callback_data="move_ساق"), InlineKeyboardButton("🏃 کل بدن", callback_data="move_کل بدن")],
        [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")]
    ])

# دکمه‌های برنامه مقدماتی
def basic_program_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("برنامه 1", callback_data="program_برنامه 1"), InlineKeyboardButton("برنامه 2", callback_data="program_برنامه 2")],
        [InlineKeyboardButton("برنامه 3", callback_data="program_برنامه 3"), InlineKeyboardButton("برنامه 4", callback_data="program_برنامه 4")],
        [InlineKeyboardButton("برنامه 5", callback_data="program_برنامه 5"), InlineKeyboardButton("برنامه 6", callback_data="program_برنامه 6")],
        [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")]
    ])

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name or "دوست عزیز"
    await update.message.reply_text(
        f"سلام {first_name} 👋\nیکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=main_menu_keyboard()
    )

# پردازش دکمه‌ها
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await query.edit_message_text(
            "به منوی اصلی برگشتی، یکی از گزینه‌ها را انتخاب کن:",
            reply_markup=main_menu_keyboard()
        )

    elif data == "moves":
        await query.edit_message_text(
            "لطفاً عضوی از بدن رو انتخاب کن:",
            reply_markup=moves_menu_keyboard()
        )

    elif data.startswith("move_"):
        part = data.split("_")[1]
        await query.edit_message_text(f"🔍 حرکات مربوط به {part} به‌زودی اضافه میشه...")

    elif data == "basic":
        await query.edit_message_text(
            "یکی از برنامه‌های زیر رو انتخاب کن:",
            reply_markup=basic_program_keyboard()
        )

    elif data.startswith("program_"):
        name = data.split("_", 1)[1]
        if name in basic_program_links:
            await query.message.reply_document(document=basic_program_links[name])
        else:
            await
