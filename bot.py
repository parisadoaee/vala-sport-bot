import json
import os
import nest_asyncio
import arabic_reshaper
from fpdf.enums import XPos, YPos
from bidi.algorithm import get_display
from fpdf import FPDF
from telegram import Update, InputFile, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from fastapi import FastAPI, Request
from telegram.ext import AIORateLimiter
import uvicorn
from fastapi.responses import JSONResponse

nest_asyncio.apply()

DATA_FILE = "users.json"
ARCHIVE_FILE = "archive.json"
user_data = {}
temp_users = {}

# مسیر گیف‌ها در پوشه static
cardio_gifs = {
    "day1": [
        "static/weight loss_day1 (1).mp4",
        "static/weight loss_day1 (2).mp4",
        "static/weight loss_day1 (3).mp4",
    ],
    "day2": [
        "static/weight loss_day2 (1).mp4",
        "static/weight loss_day2 (2).mp4",
        "static/weight loss_day2 (3).mp4",
    ],
    "day3": [
        "static/weight loss_day3 (1).mp4",
        "static/weight loss_day3 (2).mp4",
        "static/weight loss_day3 (3).mp4",
    ],
    "day4": [
        "static/weight loss_day4 (1).mp4",
        "static/weight loss_day4 (2).mp4",
        "static/weight loss_day4 (3).mp4",
    ],
}

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def archive_user(user_id):
    archive = {}
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
            archive = json.load(f)
    archive[user_id] = user_data[user_id]
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

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

# ======= تابع start با دکمه Start ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📋 برنامه ورزشی", "🥗 رژیم غذایی"],
        ["🕒 زمان‌بندی", "💬 پشتیبانی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("یکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

# ======= تابع reset برای حذف اطلاعات ========

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id in user_data:
        del user_data[user_id]
        save_data()
        await update.message.reply_text("✅ اطلاعاتت پاک شد. دوباره /start رو بزن.")
    else:
        await update.message.reply_text("اطلاعاتی برای حذف وجود نداره.")

# ======= هندلر پیام‌ها ========

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    # انتخاب برنامه ورزشی
    if text == "📋 برنامه ورزشی":
        if user_id in user_data:
            await update.message.reply_text("👀 شما قبلاً ثبت‌نام کردی. آیا می‌خوای اطلاعاتت رو تغییر بدی؟ (بله / نه)")
            temp_users[user_id] = True
        else:
            user_data[user_id] = {
                "first_name": update.message.from_user.first_name,
                "username": update.message.from_user.username or "بدون‌نام‌کاربری"
            }
            save_data()
            await update.message.reply_text("لطفاً سنت رو وارد کن 🧓 (عدد)")
        return

    # انتخاب روزهای تمرین هوازی
    if text in ["🏃‍♂️ روز اول", "🏃‍♂️ روز دوم", "🏃‍♂️ روز سوم", "🏃‍♂️ روز چهارم"]:
        day_map = {
            "🏃‍♂️ روز اول": "day1",
            "🏃‍♂️ روز دوم": "day2",
            "🏃‍♂️ روز سوم": "day3",
            "🏃‍♂️ روز چهارم": "day4",
        }
        selected_day = day_map[text]
        context.user_data["cardio_day"] = selected_day
        context.user_data["gif_index"] = 0

        gif_path = cardio_gifs[selected_day][0]
        with open(gif_path, "rb") as f:
            await update.message.reply_video(f)

        keyboard = ReplyKeyboardMarkup([["⏭ Next", "✅ Done"], ["🔙 بازگشت به صفحه قبل"]], resize_keyboard=True)
        await update.message.reply_text(f"تمرین روز {text[-2:]} - ویدیوی 1 از 3", reply_markup=keyboard)
        context.user_data["state"] = "cardio_in_progress"
        return

    # در حین تمرین هوازی
    if context.user_data.get("state") == "cardio_in_progress":
        day = context.user_data.get("cardio_day")
        idx = context.user_data.get("gif_index", 0)

        if text == "✅ Done":
            await update.message.reply_text("👏 آفرین! تمرینت تموم شد.")
            context.user_data.clear()
            keyboard = ReplyKeyboardMarkup([
                ["🏃‍♂️ روز اول", "🏃‍♂️ روز دوم"],
                ["🏃‍♂️ روز سوم", "🏃‍♂️ روز چهارم"]
            ], resize_keyboard=True)
            await update.message.reply_text("✅ می‌تونی یه روز دیگه رو هم تمرین کنی:", reply_markup=keyboard)

        elif text == "⏭ Next":
            idx += 1
            if idx >= len(cardio_gifs[day]):
                await update.message.reply_text("🎉 تمرینات روز تموم شد!")
                context.user_data.clear()
                keyboard = ReplyKeyboardMarkup([
                    ["🏃‍♂️ روز اول", "🏃‍♂️ روز دوم"],
                    ["🏃‍♂️ روز سوم", "🏃‍♂️ روز چهارم"]
                ], resize_keyboard=True)
                await update.message.reply_text("✅ می‌تونی یه روز دیگه رو انتخاب کنی:", reply_markup=keyboard)
            else:
                context.user_data["gif_index"] = idx
                gif_path = cardio_gifs[day][idx]
                with open(gif_path, "rb") as f:
                    await update.message.reply_animation(f)
                await update.message.reply_text(f"تمرین روز {day[-1]} - ویدیوی {idx+1} از 3")

        elif text == "🔙 بازگشت به صفحه قبل":
            keyboard = ReplyKeyboardMarkup([
                ["🏃‍♂️ روز اول", "🏃‍♂️ روز دوم"],
                ["🏃‍♂️ روز سوم", "🏃‍♂️ روز چهارم"]
            ], resize_keyboard=True)
            await update.message.reply_text("لطفاً یه روز رو انتخاب کن:", reply_markup=keyboard)
            context.user_data.clear()

        return

    # پاسخ به سوال تغییر اطلاعات
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

    # شروع ثبت‌نام اگر اطلاعات نیست
    if user_id not in user_data:
        await update.message.reply_text("اول دستور /start رو بزن.")
        return

    user = user_data[user_id]

    # ادامه ثبت‌نام
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
        await update.message.reply_document(InputFile(open(pdf_file, "rb"), filename=pdf_file))

        if "کاهش" in user["goal"].lower():
            keyboard = [
                ["🏃‍♂️ روز اول", "🏃‍♂️ روز دوم"],
                ["🏃‍♂️ روز سوم", "🏃‍♂️ روز چهارم"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("✅ برنامه هوازی آماده‌ست. یکی از روزها رو انتخاب کن:", reply_markup=reply_markup)
            context.user_data["state"] = "cardio_selected"
        else:
            await update.message.reply_text("اگه خواستی دوباره برنامه بگیری، دستور /start رو بزن 😊")

        archive_user(user_id)
        del user_data[user_id]
        save_data()
        os.remove(pdf_file)

# ======= FastAPI اپلیکیشن ========

load_data()
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = "https://vala-sport-bot.onrender.com" + WEBHOOK_PATH

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).rate_limiter(AIORateLimiter()).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("reset", reset))
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
    print("📩 پیام دریافتی:", data)
    await application.process_update(Update.de_json(data, application.bot))
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
