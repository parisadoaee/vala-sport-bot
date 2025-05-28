import json
import os
import nest_asyncio
import arabic_reshaper
from fpdf.enums import XPos, YPos
from bidi.algorithm import get_display
from fpdf import FPDF
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from fastapi import FastAPI, Request
from telegram.ext import AIORateLimiter
import uvicorn

nest_asyncio.apply()

DATA_FILE = "users.json"
ARCHIVE_FILE = "archive.json"
user_data = {}
temp_users = {}

# بارگذاری اطلاعات
def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)

# ذخیره اطلاعات جاری
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

# انتقال به آرشیو
def archive_user(user_id):
    archive = {}
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
            archive = json.load(f)
    archive[user_id] = user_data[user_id]
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

# ساخت PDF
def reshape(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def create_pdf(user):
    filename = f"{user['first_name']}_program.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Vazir", "", "Vazirmatn-Regular.ttf")
    pdf.set_font("Vazir", size=14)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_right_margin(10)
    pdf.set_left_margin(10)

    lines = [
        f"مشخصات شما:",
        f"سن: {user['age']}",
        f"وزن: {user['weight']} کیلوگرم",
        f"قد: {user['height']} سانتی‌متر",
        f"هدف: {user['goal']}",
        "",
        "برنامه پیشنهادی:"
    ]

    goal = user['goal'].lower()
    if "کاهش" in goal:
        plan = "۴ روز در هفته تمرین هوازی + رژیم کم‌کالری."
    elif "حجم" in goal:
        plan = "تمرین قدرتی ۵ روز در هفته + رژیم پروتئین بالا."
    else:
        plan = "ترکیبی از تمرینات مقاومتی و هوازی، ۳ تا ۴ روز در هفته."

    lines.append(plan)

    for line in lines:
        pdf.cell(0, 10, reshape(line), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(filename)
    return filename

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    first_name = update.message.from_user.first_name
    username = update.message.from_user.username or "بدون‌نام‌کاربری"

    if user_id in user_data:
        temp_users[user_id] = True
        await update.message.reply_text("👀 شما قبلاً ثبت‌نام کردی. آیا می‌خوای اطلاعاتت رو تغییر بدی؟ (بله / نه)")
    else:
        user_data[user_id] = {"first_name": first_name, "username": username}
        save_data()
        await update.message.reply_text(f"سلام {first_name}! 👋 لطفاً سنت رو وارد کن 🧓 (عدد)")

# دستور /reset
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id in user_data:
        del user_data[user_id]
        save_data()
        await update.message.reply_text("✅ اطلاعاتت پاک شد. دوباره /start رو بزن.")
    else:
        await update.message.reply_text("اطلاعاتی برای حذف وجود نداره.")

# بررسی پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    if user_id in temp_users:
        if "بله" in text:
            del user_data[user_id]
            del temp_users[user_id]
            await update.message.reply_text("اطلاعات قبلی حذف شد. لطفاً سنت رو وارد کن:")
            return
        else:
            await update.message.reply_text("خب پس با اطلاعات قبلی ادامه بده یا اگر خواستی تغییر بدی، دستور /reset رو بزن.")
            del temp_users[user_id]
            return

    if user_id not in user_data:
        await update.message.reply_text("اول دستور /start رو بزن.")
        return

    user = user_data[user_id]

    if "age" not in user:
        if not text.isdigit():
            await update.message.reply_text("سنت رو به عدد وارد کن.")
            return
        user["age"] = int(text)
        save_data()
        await update.message.reply_text("الان وزنت چقدره؟ ⚖️ (کیلوگرم)")
    elif "weight" not in user:
        if not text.isdigit():
            await update.message.reply_text("وزنت رو به عدد وارد کن.")
            return
        user["weight"] = int(text)
        save_data()
        await update.message.reply_text("قدت رو بگو چقدره؟ 📏 (سانتی‌متر)")
    elif "height" not in user:
        if not text.isdigit():
            await update.message.reply_text("قدت رو به عدد وارد کن.")
            return
        user["height"] = int(text)
        save_data()
        await update.message.reply_text("هدفت از ورزش چیه؟ 🎯 (مثلاً کاهش وزن، افزایش حجم یا تناسب اندام)")
    elif "goal" not in user:
        user["goal"] = text
        save_data()

        pdf_file = create_pdf(user)
        await update.message.reply_text("✅ مشخصاتت ثبت شد! اینم برنامه‌ت:")

        await update.message.reply_document(
            InputFile(open(pdf_file, "rb"), filename=pdf_file)
        )

        archive_user(user_id)
        del user_data[user_id]
        save_data()
        os.remove(pdf_file)

# راه‌اندازی Webhook با FastAPI
load_data()
TOKEN = "7734476012:AAEeYTo5gQoyQHYJm6cZrT2ZwmRrnBV3uD8"  # 🔐 توکن رباتت رو اینجا بذار
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = "https://vala-sport-bot.onrender.com" + WEBHOOK_PATH  # 🔗 آدرس سایتت روی Render

# تعریف FastAPI و Bot
app = FastAPI()
application = ApplicationBuilder().token(TOKEN).rate_limiter(AIORateLimiter()).build()

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("reset", reset))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# تابع async برای init و webhook
@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    await application.start()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    print("📩 پیام دریافتی:", data)  # ← این خط برای تست
    await application.process_update(Update.de_json(data, application.bot))

    return {"status": "ok"}

