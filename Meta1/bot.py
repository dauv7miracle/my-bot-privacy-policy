from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8040613052:AAHiUF3nNaLdD4DRmRtr-yuZF_j2lHqYDIU'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Web App button in message input (reply keyboard)
    webapp_keyboard = [
        [KeyboardButton(
            text="Orbitting Your Life",
            web_app=WebAppInfo(url="https://v0-new-project-thf7ga9iu43.vercel.app/")
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(webapp_keyboard, resize_keyboard=True)

    # Inline buttons in message body
    inline_buttons = [
        [InlineKeyboardButton("Contact Us", url="https://v0-new-project-thf7ga9iu43.vercel.app/")],
        [InlineKeyboardButton("Join the Club", url="https://v0-new-project-thf7ga9iu43.vercel.app/")],
        [InlineKeyboardButton("Horizon View", url="https://v0-new-project-thf7ga9iu43.vercel.app/")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

    # ✅ Send a GIF
    await update.message.reply_animation(
        animation="https://videocdn.cdnpk.net/videos/9c587712-ce33-5ce0-8162-9cc2c6ab5f8c/vertical/previews/clear/large.mp4?token=exp=1749573746~hmac=cc7c39af98c4a156010b0d0ddfbf695825af1c1e3c20347c27ed37b42918d902",  # Replace if needed
        caption="Revolved Around You",
        reply_markup=inline_markup  # Attach inline keyboard to the GIF message
    )

    # ✅ Activate Web App button in the message input area
    await update.message.reply_text(
        "Need anything else?",  # Just sending a blank to trigger reply keyboard without extra message
        reply_markup=reply_markup
    )

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
