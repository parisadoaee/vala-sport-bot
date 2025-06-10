from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = "https://vala-sport-bot.onrender.com" + WEBHOOK_PATH

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

# فقط یک دکمه ReplyKeyboard ثابت
reply_keyboard = [["📋 منو"]]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

# لینک‌های PDF برنامه‌های مقدماتی
basic_program_links = {
    "برنامه 1": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program1.pdf",
    "برنامه 2": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program2.pdf",
    "برنامه 3": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program3.pdf",
    "برنامه 4": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program4.pdf",
    "برنامه 5": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program5.pdf",
    "برنامه 6": "https://github.com/parisadoaee/vala-sport-bot/raw/main/basic%20program/basic%20program6.pdf",
}

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\nبرای نمایش منو روی دکمه زیر بزن:",
        reply_markup=reply_markup
    )

# پردازش پیام های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "📋 منو":
        inline_keyboard = [
            [InlineKeyboardButton("💬 مشاوره", callback_data="مشاوره"),
             InlineKeyboardButton("👛 کیف پول", callback_data="کیف پول")],
            [InlineKeyboardButton("🏃 حرکات", callback_data="حرکات"),
             InlineKeyboardButton("📘 مقدماتی", callback_data="مقدماتی")],
            [InlineKeyboardButton("🔰 پایه", callback_data="پایه"),
             InlineKeyboardButton("🚀 پیشرفته", callback_data="پیشرفته")]
        ]
        reply_markup_inline = InlineKeyboardMarkup(inline_keyboard)
        await update.message.reply_text("منو رو انتخاب کن 👇", reply_markup=reply_markup_inline)
    else:
        await update.message.reply_text("لطفاً روی دکمه‌ها کلیک کن ⬇️")

# هندلر دکمه‌های اینلاین
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "مشاوره":
        await query.edit_message_text(
            "برای مشاوره با پریسا کلیک کن:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ارتباط با پریسا 💬", url="https://t.me/parisad1368")],
                 [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="بازگشت")]]
            )
        )
    elif query.data == "کیف پول":
        await query.edit_message_text("💰 موجودی شما: ۰ تومان",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="بازگشت")]]))

    elif query.data == "مقدماتی":
        keyboard = [
            [InlineKeyboardButton("برنامه 1", url=basic_program_links["برنامه 1"]),
             InlineKeyboardButton("برنامه 2", url=basic_program_links["برنامه 2"])],
            [InlineKeyboardButton("برنامه 3", url=basic_program_links["برنامه 3"]),
             InlineKeyboardButton("برنامه 4", url=basic_program_links["برنامه 4"])],
            [InlineKeyboardButton("برنامه 5", url=basic_program_links["برنامه 5"])],
            [InlineKeyboardButton("برنامه 6", url=basic_program_links["برنامه 6"])],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="بازگشت")]
        ]
        await query.edit_message_text("برنامه‌ای رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "بازگشت":
        await handle_message(update, context)

    else:
        await query.edit_message_text(f"شما {query.data} رو انتخاب کردید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="بازگشت")]]))

# ثبت هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(handle_callback))

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
