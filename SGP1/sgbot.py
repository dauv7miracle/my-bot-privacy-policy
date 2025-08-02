from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8000366595:AAHQc8rdjgbn0UFQaxags6V5qakvvapqAWU'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Web App button (reply keyboard)
    webapp_keyboard = [
        [KeyboardButton(
            text="📋 List To Claim Free Credit",
            web_app=WebAppInfo(url="https://sggaming.vip/")
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(webapp_keyboard, resize_keyboard=True)

    # Inline buttons (inside message)
    inline_buttons = [[
        InlineKeyboardButton("📝 SIGNUP", url="https://tinyurl.com/FCBotTLG"),
        InlineKeyboardButton("AMOIMOVI🎬", url="https://tinyurl.com/AVBotTLG"),
        InlineKeyboardButton("SG GROUPS📱", url="https://t.me/SGGFreeGroup")
    ]]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

    # Send GIF with inline buttons
    await context.bot.send_animation(
    chat_id=update.effective_chat.id,
    animation="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWIyNzNmNHlldGEzanA2Zzg4N3NiZXNrYm9wd2FjbGVjeHhsbjU4ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/TIa4pWySR8JXXVBHyg/giphy.gif",  # Replace if needed
        caption=(
            "🇸🇬SG Gaming Partnership🇸🇬\n"
            "✨Free Credit Up SGD388+\n"
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
