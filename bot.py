from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
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

# دکمه‌ها به صورت InlineKeyboardButton تعریف میشن

def build_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("💬 مشاوره", callback_data="consult")],
        [InlineKeyboardButton("👛 کیف پول", callback_data="wallet"),
         InlineKeyboardButton("🏃 حرکات", callback_data="moves")],
        [InlineKeyboardButton("🔰 پایه", callback_data="basic"),
         InlineKeyboardButton("🚀 پیشرفته", callback_data="advanced"),
         InlineKeyboardButton("📘 مقدماتی", callback_data="basic_program")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_moves_keyboard():
    keyboard = [
        [InlineKeyboardButton("🖐️ دست", callback_data="move_hand"),
         InlineKeyboardButton("🦵 پا", callback_data="move_leg"),
         InlineKeyboardButton("💪 شانه", callback_data="move_shoulder")],
        [InlineKeyboardButton("❤️ سینه", callback_data="move_chest"),
         InlineKeyboardButton("🏋️‍♂️ شکم", callback_data="move_abs"),
         InlineKeyboardButton("🦴 پشت", callback_data="move_back")],
        [InlineKeyboardButton("🦶 ساق", callback_data="move_calf"),
         InlineKeyboardButton("🏃 کل بدن", callback_data="move_fullbody")],
        [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_basic_program_keyboard():
    keyboard = [
        [InlineKeyboardButton("برنامه 1", callback_data="program1"),
         InlineKeyboardButton("برنامه 2", callback_data="program2")],
        [InlineKeyboardButton("برنامه 3", callback_data="program3"),
         InlineKeyboardButton("برنامه 4", callback_data="program4")],
        [InlineKeyboardButton("برنامه 5", callback_data="program5"),
         InlineKeyboardButton("برنامه 6", callback_data="program6")],
        [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.from_user.first_name or "دوست عزیز"
    reply_markup = build_main_keyboard()
    await update.message.reply_text(f"سلام {first_name} 👋\nیکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

# هندلر برای کلیک روی دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # حتما پاسخ بدهیم به تلگرام

    data = query.data

    if data == "main_menu":
        reply_markup = build_main_keyboard()
        await query.edit_message_text("به منوی اصلی برگشتی، یکی از گزینه‌ها را انتخاب کن:", reply_markup=reply_markup)

    elif data == "moves":
        reply_markup = build_moves_keyboard()
        await query.edit_message_text("لطفاً عضوی از بدن رو انتخاب کن:", reply_markup=reply_markup)

    elif data.startswith("move_"):
        part = data.replace("move_", "")
        await query.edit_message_text(f"حرکات مربوط به {part} را اینجا نمایش می‌دهیم.")

    elif data == "basic_program":
        reply_markup = build_basic_program_keyboard()
        await query.edit_message_text("یکی از برنامه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

    elif data.startswith("program"):
        link_key = {
            "program1": "برنامه 1",
            "program2": "برنامه 2",
            "program3": "برنامه 3",
            "program4": "برنامه 4",
            "program5": "برنامه 5",
            "program6": "برنامه 6",
        }[data]
        pdf_link = basic_program_links.get(link_key)
        if pdf_link:
            await context.bot.send_document(chat_id=query.message.chat_id, document=pdf_link)

    elif data == "consult":
        keyboard = [[InlineKeyboardButton("ارتباط با پریسا 💬", url="https://t.me/parisad1368")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("برای دریافت مشاوره مستقیم، روی دکمه زیر کلیک کن:", reply_markup=reply_markup)

    else:
        await query.edit_message_text("لطفاً یکی از گزینه‌های موجود را انتخاب کن.")

# هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

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
