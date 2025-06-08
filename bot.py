from telegram import Update, ReplyKeyboardMarkup
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

# منوی اصلی
main_keyboard = [
    ["💬 مشاوره", "👛 کیف پول", "🏃 حرکات"],
    ["🔰 پایه", "🚀 پیشرفته", "📘 مقدماتی"]
]

# منوی حرکات اعضای بدن
moves_keyboard = [
    ["🖐️ دست", "🦵 پا", "💪 شانه"],
    ["❤️ سینه", "🏋️‍♂️ شکم", "🦴 پشت"],
    ["🦶 ساق", "🏃 کل بدن"],
    ["🏠 بازگشت به منوی اصلی"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.from_user.first_name or "دوست عزیز"
    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    await update.message.reply_text(f"سلام {first_name} 👋\nیکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🏃 حرکات":
        reply_markup = ReplyKeyboardMarkup(moves_keyboard, resize_keyboard=True)
        await update.message.reply_text("لطفاً عضوی از بدن رو انتخاب کن:", reply_markup=reply_markup)
        return

    elif text in ["🖐️ دست", "🦵 پا", "💪 شانه", "❤️ سینه", "🏋️‍♂️ شکم", "🦴 پشت", "🦶 ساق", "🏃 کل بدن"]:
        await update.message.reply_text(f"حرکات مربوط به {text} را اینجا نمایش می‌دهیم.")
        return

    elif text == "🏠 بازگشت به منوی اصلی":
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        await update.message.reply_text("به منوی اصلی برگشتی، یکی از گزینه‌ها را انتخاب کن:", reply_markup=reply_markup)
        return

    else:
        await update.message.reply_text("لطفاً یکی از گزینه‌های موجود را انتخاب کن.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

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
