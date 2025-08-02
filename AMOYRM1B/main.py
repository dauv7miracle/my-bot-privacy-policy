import os
from fastapi import FastAPI, Request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import defaults

# Get token from environment
TOKEN = os.getenv("7533261270:AAG236zlDbmrxDRyfgX25I0PAItR7THyx_M")

# Telegram bot setup
application = Application.builder().token(TOKEN).build()

# FastAPI app
fastapi_app = FastAPI()


# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    webapp_keyboard = [
        [KeyboardButton(
            text="New Updated Amoi Collection",
            web_app=WebAppInfo(url="https://tinyurl.com/TLGFREERM")
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(webapp_keyboard, resize_keyboard=True)

    inline_buttons = [
        [InlineKeyboardButton("AmoiMovi 🔞", url="https://t.me/FreecreditRM168")],
        [InlineKeyboardButton("LucahMovi 💦", url="https://t.me/RMFreeKredit")],
        [InlineKeyboardButton("TelegramMovi 💦", url="https://t.me/+fzUyKw1OMlAyMWVl")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

    # Send photo
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://i.imgur.com/ER7HlsY.png",  # Use online photo URL, not local file path
        caption=(
            "⭐Join AmoiMovi Kat Bawah Link✅\n"
            '<a href="https://tinyurl.com/TLGFREERM">Click Here to Watch🔄</a>'
        ),
        parse_mode="HTML",
        reply_markup=inline_markup
    )

    # Send reply keyboard
    await update.message.reply_text("Klik bawah untuk koleksi terkini 👇", reply_markup=reply_markup)


# Optional handler
async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Watch Now", url="https://tinyurl.com/TIGFREEMA")]
    ])
    await update.message.reply_text("⚠️ Click The Below Button to Watch AmoiMovi", reply_markup=reply_markup)


# Add handlers
application.add_handler(CommandHandler("start", start))


# Webhook endpoint for Telegram
@fastapi_app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}


# Optional health check
@fastapi_app.get("/")
async def root():
    return {"status": "Bot is running on Deta Space"}
