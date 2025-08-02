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

TOKEN = '8098330881:AAGDe8k07MlYS3ehN06za-y6iPkgUBA-Ldw'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user(update, "pgk3")
    # Web App button (reply keyboard)
    webapp_keyboard = [
        [KeyboardButton(
            text="📋 List To Claim Free Credit",
            web_app=WebAppInfo(url="https://tinyurl.com/mr2nj42a")
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(webapp_keyboard, resize_keyboard=True)

    # Inline buttons (inside message)
    inline_buttons = [[
        InlineKeyboardButton("Free Credit Group", url="https://t.me/PNGFreeK100"),
        InlineKeyboardButton("PNG Group", url="https://t.me/addlist/XABJkWsF-dc3ZGM1?utm_medium=social&utm_source=heylink.me"),
    ]]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

    # Send GIF with inline buttons
    await context.bot.send_animation(
    chat_id=update.effective_chat.id,
    animation="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExN21rc3pxanRrdnlwNzlpZDZuMXB5dHh5d3Fjb2kxamx5d3g3OHBwYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Ar8lCwwM4EatNn2ocG/giphy.gif",  # Replace if needed
        caption=(
            "🇵🇬PNG Gaming Partnership🇵🇬\n"
            "✨Free Credit Up PGK100+\n"
            "✨Allow Play All Games\n\n"
            "✅SLOT ✅LIVE ✅FISH ✅SPORT ✅4D\n\n"
        ),
        reply_markup=inline_markup
    )

    # Send reply keyboard to show Web App button
    await update.message.reply_text(
    "⚠️Click The Below Button to Get Free Credit",
    reply_markup=reply_markup
)
       

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

#Papua New Guinea