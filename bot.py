from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
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

# دکمه‌های inline برای منوها
main_keyboard_inline = InlineKeyboardMarkup([
    [InlineKeyboardButton("💬 مشاوره", callback_data="مشاوره"), InlineKeyboardButton("👛 کیف پول", callback_data="کیف پول")],
    [InlineKeyboardButton("🏃 حرکات", callback_data="حرکات"), InlineKeyboardButton("📘 مقدماتی", callback_data="مقدماتی")],
    [InlineKeyboardButton("🔰 پایه", callback_data="پایه"), InlineKeyboardButton("🚀 پیشرفته", callback_data="پیشرفته")],
])

moves_keyboard_inline = InlineKeyboardMarkup([
    [InlineKeyboardButton("🖐️ دست", callback_data="دست"), InlineKeyboardButton("🦵 پا", callback_data="پا"), InlineKeyboardButton("💪 شانه", callback_data="شانه")],
    [InlineKeyboardButton("❤️ سینه", callback_data="سینه"), InlineKeyboardButton("🏋️‍♂️ شکم", callback_data="شکم"), InlineKeyboardButton("🦴 پشت", callback_data="پشت")],
    [InlineKeyboardButton("🦶 ساق", callback_data="ساق"), InlineKeyboardButton("🏃 کل بدن", callback_data="کل بدن")],
    [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="بازگشت اصلی")]
])

basic_program_keyboard_inline = InlineKeyboardMarkup([
    [InlineKeyboardButton("برنامه 1", callback_data="برنامه 1"), InlineKeyboardButton("برنامه 2", callback_data="برنامه 2")],
    [InlineKeyboardButton("برنامه 3", callback_data="برنامه 3"), InlineKeyboardButton("برنامه 4", callback_data="برنامه 4")],
    [InlineKeyboardButton("برنامه 5", callback_data="برنامه 5"), InlineKeyboardButton("برنامه 6", callback_data="برنامه 6")],
    [InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="بازگشت اصلی")]
])

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.from_user.first_name or "دوست عزیز"
    await update.message.reply_text(f"سلام {first_name} 👋\nیکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=main_keyboard_inline)

# هندلر برای دکمه‌های inline
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "حرکات":
        await query.edit_message_text("لطفاً عضوی از بدن رو انتخاب کن:", reply_markup=moves_keyboard_inline)

    elif data in ["دست", "پا", "شانه", "سینه", "شکم", "پشت", "ساق", "کل بدن"]:
        await query.edit_message_text(f"حرکات مربوط به {data} را اینجا نمایش می‌دهیم.", reply_markup=moves_keyboard_inline)

    elif data == "مقدماتی":
        await query.edit_message_text("یکی از برنامه‌های زیر رو انتخاب کن:", reply_markup=basic_program_keyboard_inline)

    elif data in basic_program_links:
        await context.bot.send_document(chat_id=query.message.chat_id, document=basic_program_links[data])
        # بعد از ارسال فایل، منو برنامه‌های مقدماتی رو دوباره نشون می‌دیم
        await query.edit_message_text("یکی از برنامه‌های زیر رو انتخاب کن:", reply_markup=basic_program_keyboard_inline)

    elif data == "بازگشت اصلی":
        await query.edit_message_text("به منوی اصلی برگشتی، یکی از گزینه‌ها را انتخاب کن:", reply_markup=main_keyboard_inline)

    elif data == "مشاوره":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ارتباط با پریسا 💬", url="https://t.me/parisad1368")]])
        await query.edit_message_text("برای دریافت مشاوره مستقیم، روی دکمه زیر کلیک کن:", reply_markup=keyboard)

    elif data == "کیف پول":
        await query.edit_message_text("کیف پول در حال حاضر فعال نیست.", reply_markup=main_keyboard_inline)

    elif data == "پایه":
        await query.edit_message_text("شما بخش پایه را انتخاب کردید.", reply_markup=main_keyboard_inline)

    elif data == "پیشرفته":
        await query.edit_message_text("شما بخش پیشرفته را انتخاب کردید.", reply_markup=main_keyboard_inline)

    else:
        await query.edit_message_text("لطفاً یکی از گزینه‌های موجود را انتخاب کن.", reply_markup=main_keyboard_inline)

# هندلر پیام‌های متنی (برای مواقعی که کاربر تایپ کنه)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً از دکمه‌های زیر استفاده کن.")

# اضافه کردن هندلرها
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
