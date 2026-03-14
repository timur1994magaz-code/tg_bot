import os
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)
import gspread
from google.oauth2.service_account import Credentials

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID_HERE")
NOTIFY_CHAT_ID = os.environ.get("NOTIFY_CHAT_ID", "")  # твой Telegram ID для уведомлений

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_sheet():
     creds_dict = json.loads(os.environ.get("GOOGLE_CREDENTIALS_JSON"))
   creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1

Q1, Q2, Q3, Q4, Q5, GET_PHONE, GET_EMAIL = range(7)

Q1_OPTIONS = [
    ["👤 Фрилансер / самозанятый"],
    ["🏢 Владелец бизнеса"],
    ["📊 Маркетолог / SMM в найме"],
    ["🤔 Просто интересно"],
]

Q2_OPTIONS = [
    ["💰 Хочу 150–250к+ в месяц"],
    ["🚪 Устал(а) работать за копейки"],
    ["🔍 Хочу разобраться в AI-видео"],
    ["👀 Пока просто смотрю"],
]

Q3_OPTIONS = [
    ["✅ Готов(а) начать за 1–2 недели"],
    ["🤔 Сначала хочу разобраться"],
    ["❓ Пока не уверен(а)"],
]

Q4_OPTIONS = [
    ["⚡ 5–10 часов и больше"],
    ["⏳ 2–5 часов в неделю"],
    ["😔 Меньше 2 часов"],
]

SCORE_MAP = {
    "👤 Фрилансер / самозанятый": 2,
    "🏢 Владелец бизнеса": 2,
    "📊 Маркетолог / SMM в найме": 1,
    "🤔 Просто интересно": 0,
    "💰 Хочу 150–250к+ в месяц": 2,
    "🚪 Устал(а) работать за копейки": 2,
    "🔍 Хочу разобраться в AI-видео": 1,
    "👀 Пока просто смотрю": 0,
    "✅ Готов(а) начать за 1–2 недели": 2,
    "🤔 Сначала хочу разобраться": 1,
    "❓ Пока не уверен(а)": 0,
    "⚡ 5–10 часов и больше": 2,
    "⏳ 2–5 часов в неделю": 1,
    "😔 Меньше 2 часов": 0,
}

def score_to_label(score):
    if score >= 7:
        return "🔥 Горячий"
    elif score >= 4:
        return "🌤 Тёплый"
    else:
        return "❄️ Холодный"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["tg_username"] = f"@{update.effective_user.username}" if update.effective_user.username else "нет username"
    context.user_data["tg_name"] = update.effective_user.full_name
    context.user_data["score"] = 0

    await update.message.reply_text(
        "👋 Привет! Это анкета для записи на персональную консультацию по AI-видео для бизнеса.\n\n"
        "Займёт всего 90 секунд ⏱\n\n"
        "После анкеты — запишем тебя на разбор, где покажу как выйти на 250 000 ₽/мес и выше на AI-роликах.\n\n"
        "_Всего 5 вопросов + контакты — и всё готово_ 👇",
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "❓ *Вопрос 1 из 5*\n\nКто ты сейчас? Выбери ближайшее 👇",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(Q1_OPTIONS, resize_keyboard=True, one_time_keyboard=True),
    )
    return Q1

async def q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.message.text
    context.user_data["q1"] = ans
    context.user_data["score"] += SCORE_MAP.get(ans, 0)

    await update.message.reply_text(
        "❓ *Вопрос 2 из 5*\n\nЧто для тебя сейчас самое важное?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(Q2_OPTIONS, resize_keyboard=True, one_time_keyboard=True),
    )
    return Q2

async def q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.message.text
    context.user_data["q2"] = ans
    context.user_data["score"] += SCORE_MAP.get(ans, 0)

    await update.message.reply_text(
        "❓ *Вопрос 3 из 5*\n\nЕсли на консультации ты увидишь чёткий путь к результату — готов(а) начать?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(Q3_OPTIONS, resize_keyboard=True, one_time_keyboard=True),
    )
    return Q3

async def q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.message.text
    context.user_data["q3"] = ans
    context.user_data["score"] += SCORE_MAP.get(ans, 0)

    await update.message.reply_text(
        "❓ *Вопрос 4 из 5*\n\nСколько времени в неделю готов(а) выделить на обучение и практику?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(Q4_OPTIONS, resize_keyboard=True, one_time_keyboard=True),
    )
    return Q4

async def q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.message.text
    context.user_data["q4"] = ans
    context.user_data["score"] += SCORE_MAP.get(ans, 0)

    await update.message.reply_text(
        "❓ *Вопрос 5 из 5*\n\nПочему именно сейчас ты хочешь разобраться в AI-видео? Напиши в 1–2 предложениях 👇",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return Q5

async def q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q5"] = update.message.text

    await update.message.reply_text(
        "Отлично! Почти готово 🙌\n\n"
        "📱 *Напиши свой номер телефона* (в формате +79XXXXXXXXX)",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    context.user_data["phone"] = phone

    await update.message.reply_text(
        "📧 *И напоследок — укажи свою почту:*",
        parse_mode="Markdown",
    )
    return GET_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    context.user_data["email"] = email

    ud = context.user_data
    score = ud.get("score", 0)
    label = score_to_label(score)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    row = [
        now,
        ud.get("tg_name", ""),
        ud.get("tg_username", ""),
        ud.get("phone", ""),
        ud.get("email", ""),
        ud.get("q1", ""),
        ud.get("q2", ""),
        ud.get("q3", ""),
        ud.get("q4", ""),
        ud.get("q5", ""),
        score,
        label,
    ]

    try:
        sheet = get_sheet()
        sheet.append_row(row)
        logger.info(f"Новая запись добавлена: {ud.get('tg_username')}")
    except Exception as e:
        logger.error(f"Ошибка записи в таблицу: {e}")

    if NOTIFY_CHAT_ID:
        try:
            notify_text = (
                f"🆕 *Новая анкета!*\n\n"
                f"👤 {ud.get('tg_name')} ({ud.get('tg_username')})\n"
                f"📱 {ud.get('phone')}\n"
                f"📧 {ud.get('email')}\n"
                f"📊 Скор: {score}/8 — {label}\n\n"
                f"*Q1:* {ud.get('q1')}\n"
                f"*Q2:* {ud.get('q2')}\n"
                f"*Q3:* {ud.get('q3')}\n"
                f"*Q4:* {ud.get('q4')}\n"
                f"*Q5:* {ud.get('q5')}"
            )
            await context.bot.send_message(
                chat_id=NOTIFY_CHAT_ID,
                text=notify_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления: {e}")

    await update.message.reply_text(
        "🎉 *Анкета принята!*\n\n"
        "Я свяжусь с тобой в ближайшее время и запишем на консультацию.\n\n"
        "Пока можешь посмотреть мои последние AI-ролики в профиле 👆",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Анкета отменена. Если захочешь вернуться — просто напиши /start",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, q1)],
            Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, q2)],
            Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, q3)],
            Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, q4)],
            Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, q5)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
