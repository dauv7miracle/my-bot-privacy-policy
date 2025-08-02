from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '7774301666:AAFMNx01oRoMNG7jOEyzhuKMdr74U-iDVoE'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        [InlineKeyboardButton("TelegramMovi 💦", url="https://t.me/+fzUyKw1OMlAyMWVl")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)


# Send photo with inline buttons
    await context.bot.send_photo(
    chat_id=update.effective_chat.id,
    photo=r'C:\Users\User\Downloads\3AE46A9D-F615-4454-A50D-55AB6E27F52E.jpg',
    caption=(
        "⭐Join AmoiMovi Kat Bawah Link✅\n"
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