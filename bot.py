from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
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

# کلیدهای منوی اصلی
main_inline_buttons = [
    [InlineKeyboardButton("💬 مشاوره", callback_data="consultation")],
    [InlineKeyboardButton("👛 کیف پول", callback_data="wallet")],
    [InlineKeyboardButton("🏃 حرکات", callback_data="moves")],
    [InlineKeyboardButton("📘 مقدماتی", callback_data="basic_program")],
    [InlineKeyboardButton("🔰 پایه", callback_data="basic_level")],
    [InlineKeyboardButton("🚀 پیشرفته", callback_data="advanced_level")]
]

# دکمه‌های حرکات
moves_inline_buttons = [
    [InlineKeyboardButton("🖐️ دست", callback_data="move_hand"), InlineKeyboardButton("🦵 پا", callback_data="move_leg"), InlineKeyboardButton("💪 شانه", callback_data="move_shoulder")],
    [InlineKeyboardButton("❤️ سینه", callback_data="move_chest"), InlineKeyboardButton("🏋️‍♂️ شکم", callback_data="move_abs"), InlineKeyboardButton("🦴 پشت", callback_data="move_back")],
    [InlineKeyboardButton("🦶 ساق", callback_data="move_calf"), InlineKeyboardButton("🏃 کل بدن", callback_data="move_fullbody")],
    [InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]
]

# دکمه‌های برنامه‌های مقدماتی
basic_program_inline_buttons = [
    [InlineKeyboardButton("برنامه 1", callback_data="basic_program1"), InlineKeyboardButton("برنامه 2", callback_data="basic_program2")],
    [InlineKeyboardButton("برنامه 3", callback_data="basic_program3"), InlineKeyboardButton("برنامه 4", callback_data="basic_program4")],
    [InlineKeyboardButton("برنامه 5", callback_data="basic_program5"), InlineKeyboardButton("برنامه 6", callback_data="basic_program6")],
    [InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]
]

# پاسخ‌های حرکات بدن
moves_text = {
    "move_hand": "حرکات مربوط به دست را اینجا نمایش می‌دهیم.",
    "move_leg": "حرکات مربوط به پا را اینجا نمایش می‌دهیم.",
    "move_shoulder": "حرکات مربوط به شانه را اینجا نمایش می‌دهیم.",
    "move_chest": "حرکات مربوط به سینه را اینجا نمایش می‌دهیم.",
    "move_abs": "حرکات مربوط به شکم را اینجا نمایش می‌دهیم.",
    "move_back": "حرکات مربوط به پشت را اینجا نمایش می‌دهیم.",
    "move_calf": "حرکات مربوط به ساق را اینجا نمایش می‌دهیم.",
    "move_fullbody": "حرکات کل بدن را اینجا نمایش می‌دهیم."
}

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.from_user.first_name or "دوست عزیز"
    await update.message.reply_text(
        f"سلام {first_name} 👋\nیکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(main_inline_buttons)
    )
    await update.message.reply_text(" ", reply_markup=ReplyKeyboardRemove())

# هندل دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        await query.message.edit_text(
            "یکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(main_inline_buttons)
        )
    elif data == "consultation":
        keyboard = [[InlineKeyboardButton("ارتباط با پریسا 💬", url="https://t.me/parisad1368")],
                    [InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]]
        await query.message.edit_text(
            "برای دریافت مشاوره مستقیم، روی دکمه زیر کلیک کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "wallet":
        keyboard = [[InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]]
        await query.message.edit_text(
            "صفحه کیف پول در دست توسعه است.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "moves":
        await query.message.edit_text(
            "لطفاً عضوی از بدن رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(moves_inline_buttons)
        )
    elif data.startswith("move_"):
        text = moves_text.get(data, "حرکات مربوط به این بخش را نمایش می‌دهیم.")
        keyboard = [[InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]]
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "basic_program":
        await query.message.edit_text(
            "یکی از برنامه‌های زیر رو انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(basic_program_inline_buttons)
        )
    elif data.startswith("basic_program"):
        program_key = "برنامه " + data[-1]
        link = basic_program_links.get(program_key)
        if link:
            await query.message.reply_document(document=link)
        else:
            await query.message.edit_text(
                "برنامه مورد نظر یافت نشد.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]])
            )
    elif data == "basic_level":
        keyboard = [[InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]]
        await query.message.edit_text(
            "صفحه پایه در دست توسعه است.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data == "advanced_level":
        keyboard = [[InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]]
        await query.message.edit_text(
            "صفحه پیشرفته در دست توسعه است.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.message.edit_text(
            "گزینه نامشخص، لطفاً دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 بازگشت به صفحه اصلی", callback_data="back_to_main")]])
        )

# پیام متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "لطفاً یکی از گزینه‌های موجود را با دکمه‌ها انتخاب کن.",
        reply_markup=InlineKeyboardMarkup(main_inline_buttons)
    )
    await update.message.reply_text(" ", reply_markup=ReplyKeyboardRemove())

# هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI
@app.get("/")
async def root():
    return JSONResponse(content={"message": "Bot is running 🚀"})

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    await application.start()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    await application.process_update(Update.de_json(data, application.bot))
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
