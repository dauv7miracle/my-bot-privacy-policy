import os
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from datetime import datetime

# File to store user IDs
CONTACTS_FILE = "shared_contacts.txt"

# Load shared contacts from file
def load_shared_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return set()
    with open(CONTACTS_FILE, "r") as file:
        return set(line.strip() for line in file)

# Save shared contacts to file
def save_shared_contacts():
    with open(CONTACTS_FILE, "w") as file:
        for user_id in shared_contacts:
            file.write(f"{user_id}\n")

# Set to store user IDs who have shared their contact
shared_contacts = load_shared_contacts()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Check if the user has already shared their contact
    if user_id in shared_contacts:
        await send_content(update)
    else:
        # Ask for contact permission
        button = KeyboardButton("📱 Verify Phone Number", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            "Verify your phone number to continue:",
            reply_markup=keyboard
        )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user

    if contact:
        phone_number = contact.phone_number
        user_id = str(user.id)
        username = user.username or "NoUsername"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add user ID to the set and save to file
        shared_contacts.add(user_id)
        save_shared_contacts()

        # Save contact to log file
        with open("contacts_log.txt", "a", encoding="utf-8") as file:
            file.write(f"{timestamp} | {user_id} | @{username} | {phone_number}\n")

        await update.message.reply_text(f"✅ Verified! your phone number: {phone_number}")
        await send_content(update)

async def send_content(update: Update):
    # Image caption with description
    caption = (
                   "Cuba Dengan RMGROUP Sini 👍🏻 \n\n"
            '<a href="https://tinyurl.com/TRM88">🇲🇾 Register Free Credit RM20</a>\n\n'
            '<a href="tg://addlist?slug=sU_gdXU83j1hMzc1">🔥 Subscribe Telegram Free Credit</a>\n\n'
            "⬇️Tekan Start Button Masuk Klaim ⬇️"

    )

    # Inline buttons below the image
    buttons = [
        [InlineKeyboardButton("Free Credit", url="https://tinyurl.com/TRM88")],
        [InlineKeyboardButton("Touch`nGo Angpao", url="https://t.me/rmfreetng")],
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    # Send image with caption and inline buttons
    await update.message.reply_animation(
        animation="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjVpbzdpeWllNHQ3encyenpiOWw1MzY3NHhwaHNyZG50b3FsdDIwNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/NS4yQG5Ydg6P11ODN9/giphy.gif",
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


# Setup bot
app = Application.builder().token("7937387439:AAFhO0NbzYcRwD8CH9RVkdFEovNTo87UxLA").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
app.run_polling()
