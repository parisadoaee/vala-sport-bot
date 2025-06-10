from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
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

# منوهای کیبورد
main_keyboard = [
    ["💬 مشاوره", "👛 کیف پول", "🏃 حرکات"],
    ["🔰 پایه", "🚀 پیشرفته", "📘 مقدماتی"]
]

moves_keyboard = [
    ["🖐️ دست", "🦵 پا", "💪 شانه"],
    ["❤️ سینه", "🏋️‍♂️ شکم", "🦴 پشت"],
    ["🦶 ساق", "🏃 کل بدن"],
    ["🏠 بازگشت به منوی اصلی"]
]

basic_program_keyboard = [
    ["برنامه 1", "برنامه 2"],
    ["برنامه 3", "برنامه 4"],
    ["برنامه 5", "برنامه 6"],
    ["🏠 بازگشت به منوی اصلی"]
]

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.from_user.first_name or "دوست عزیز"
    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    await update.message.reply_text(f"سلام {first_name} 👋\nیکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

# پردازش پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🏃 حرکات":
        reply_markup = ReplyKeyboardMarkup(moves_keyboard, resize_keyboard=True)
        await update.message.reply_text("لطفاً عضوی از بدن رو انتخاب کن:", reply_markup=reply_markup)

    elif text in ["🖐️ دست", "🦵 پا", "💪 شانه", "❤️ سینه", "🏋️‍♂️ شکم", "🦴 پشت", "🦶 ساق", "🏃 کل بدن"]:
        await update.message.reply_text(f"حرکات مربوط به {text} را اینجا نمایش می‌دهیم.")

    elif text == "📘 مقدماتی":
        reply_markup = ReplyKeyboardMarkup(basic_program_keyboard, resize_keyboard=True)
        await update.message.reply_text("یکی از برنامه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

    elif text in basic_program_links:
        await update.message.reply_document(document=basic_program_links[text])

    elif text == "🏠 بازگشت به منوی اصلی":
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        await update.message.reply_text("به منوی اصلی برگشتی، یکی از گزینه‌ها را انتخاب کن:", reply_markup=reply_markup)

    elif text == "💬 مشاوره":
        keyboard = [[InlineKeyboardButton("ارتباط با پریسا 💬", url="https://t.me/parisad1368")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("برای دریافت مشاوره مستقیم، روی دکمه زیر کلیک کن:", reply_markup=reply_markup)

    else:
        await update.message.reply_text("لطفاً یکی از گزینه‌های موجود را انتخاب کن.")

# هندلرها
application.add_handler(CommandHandler("start", start))
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
