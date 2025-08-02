from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime
import os

def log_user(update: Update, bot_name: str):
    user = update.effective_user
    log_dir = os.path.abspath("user_logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(f"{log_dir}/{bot_name}.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | ID: {user.id} | Username: @{user.username} | Name: {user.full_name}\n")

TOKEN = '7461459120:AAGI-6-bp6MEIZ9yyUiuVJzN04CtdKhcKh8'

async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with image and buttons"""
    log_user(update, "shell1")
    
    # Inline buttons
    inline_buttons = [
        [InlineKeyboardButton("REGISTER HERE", url="https://shell99.vip/RF15611733")],
        [InlineKeyboardButton("FREE CREDIT", url="https://t.me/Shell99Bot")],    
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

    # Send photo with inline buttons
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open('shell1.jpg', 'rb'),
        caption=(
            "✨Dapatkan EXTRA BONUS UTK Member SHELL99✨\n"
            "💎 Register now and get RM7 FREE instantly!\n"
            "💎 Login everyday and get FREE BONUS!\n"
            "________________________________________\n"
            "🔥Promosi Terhebat Ada Disini🔥\n"
            "✨ Bonus Selamat Datang: 200%!\n"
            "💥 Bonus double – Lebih banyak peluang MENANG!\n\n"
            "🎁Min Depo RM1 Free RM5\n"
            "🎁Daily 50%+100% Unlimited Claim\n\n"
            "👇Register and play now‼️‼️‼️👇\n"
            '<a href="https://shell99.vip/RF15611733">Click Here to 🌐CLAIM FREE</a>'
        ),
        parse_mode="HTML",
        reply_markup=inline_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await send_welcome(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    await send_welcome(update, context)

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Handle all text messages (excludes commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()