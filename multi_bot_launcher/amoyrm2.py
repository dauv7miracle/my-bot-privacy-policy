from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import os

def log_user(update: Update, bot_name: str):
    user = update.effective_user
    log_dir = "user_logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(f"{log_dir}/{bot_name}.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | ID: {user.id} | Username: @{user.username} | Name: {user.full_name}\n")

TOKEN = '7774301666:AAFMNx01oRoMNG7jOEyzhuKMdr74U-iDVoE'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user(update, "amoyrm2")
    # Web App button (reply keyboard)
    webapp_keyboard = [
        [KeyboardButton(
            text="New Updated Amoi Collection",
            web_app=WebAppInfo(url="https://tinyurl.com/TLGFREERM")
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(webapp_keyboard, resize_keyboard=True)

    # Inline buttons (inside message)
    inline_buttons = [
        [InlineKeyboardButton("AmoiMovi 🔞", url="https://t.me/FreecreditRM168")],
        [InlineKeyboardButton("LucahMovi 💦", url="https://t.me/RMFreeKredit")],
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)


# Send photo with inline buttons
    await context.bot.send_animation(
    chat_id=update.effective_chat.id,
    animation="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOW5lYTE0MXRjNmtxMWhmM3A5djFjNm95c3hiYjgyYWlkMTRmaTZ5dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/f8ZYUN0qhfTBdhNb76/giphy.gif",  # Replace if needed
    caption=(
        "⭐Join Amoi Live Show Kat Bawah Link✅\n"
        '<a href="https://tinyurl.com/TLGFREERM">Click Here to Watch🔄</a>'
    ),
    parse_mode="HTML",
    reply_markup=inline_markup  # Make sure this is defined earlier in your code
    )

    # Send reply keyboard to show Web App button
async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # First define the reply_markup
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Watch Now", url="https://tinyurl.com/TIGFREEMA")]
    ])
    
    # Then send the message with proper indentation
    await update.message.reply_text(
        "⚠️ Click The Below Button to Watch AmoiMovi",
        reply_markup=reply_markup
    )
       

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

# Kimberly Chu