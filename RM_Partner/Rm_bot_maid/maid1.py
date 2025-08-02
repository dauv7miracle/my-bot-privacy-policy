from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)
from datetime import datetime
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8008686085:AAE3Iq1YJhWpksbo0yeuxfFgNw_4DDWH6w0"  # Replace with your bot token

WELCOME_MESSAGE = "👋 Welcome {name}! Please read group rules."
GOODBYE_MESSAGE = "👋 Goodbye {name}!"
ALLOWED_LINKS = ["telegram.org"]
MAX_WARNINGS = 3

user_warnings = {}

async def is_user_admin(update, context):
    chat = update.effective_chat
    user_id = update.message.from_user.id
    member = await chat.get_member(user_id)
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.CREATOR)

async def start(update, context):
    await update.message.reply_text("🤖 RM Group Maid Bot is active!")
    
async def welcome(update, context):
    chat_member = update.chat_member
    # Check if the user just joined
    if chat_member.new_chat_member.status in (ChatMember.MEMBER, ChatMember.RESTRICTED):
        user = chat_member.new_chat_member.user
        name = user.first_name or "Unknown"
        user_id = user.id
        username = f"@{user.username}" if user.username else "No username"
        join_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lang = getattr(user, "language_code", None)
        country = lang.upper() if lang else "Unknown"
        
        # Send welcome message
        await update.effective_chat.send_message(
            WELCOME_MESSAGE.format(name=name)
        )

        # Log to file
        log_entry = f"{join_time} | ID: {user_id} | Username: {username} | Country: {country}\n"
        with open("join_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)

async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.chat_member.old_chat_member.user
    name = left_member.first_name
    await update.effective_chat.send_message(GOODBYE_MESSAGE.format(name=name))

async def delete_message_callback(context):
    job_data = context.job.data
    await context.bot.delete_message(job_data["chat_id"], job_data["message_id"])

async def clean_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.new_chat_members or message.left_chat_member:
        # Schedule deletion after 30 seconds
        context.job_queue.run_once(
            delete_message_callback,
            30,
            data={
                "chat_id": message.chat_id,
                "message_id": message.message_id
            }
        )

async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id

    user_warnings[user.id] = user_warnings.get(user.id, 0) + 1
    warnings_left = MAX_WARNINGS - user_warnings[user.id]
    
    if warnings_left > 0:
        await context.bot.send_message(
            chat_id,
            f"⚠️ Warning to {user.first_name} ({user_warnings[user.id]}/{MAX_WARNINGS})!\n"
            f"Next violation will result in ban."
        )
    else:
        await context.bot.ban_chat_member(chat_id, user.id)
        await context.bot.send_message(
            chat_id,
            f"🚫 Banned {user.first_name} for repeated violations"
        )
        del user_warnings[user.id]

# FIXED link checking function
async def check_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text.lower()

    # Check if sender is admin (including anonymous admins)
    if await is_admin(update):
        return  # Admins (including anonymous) can send any links

    # Check for links
    has_link = "http://" in text or "https://" in text or "www." in text
    if not has_link:
        return

    # Check if it contains any allowed domain
    has_allowed_link = any(domain in text for domain in ALLOWED_LINKS)

    # If message contains links but no allowed links, delete only
    if not has_allowed_link:
        try:
            await message.delete()
            # No warning message
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            
async def is_admin(update: Update):
    if not update.message or not update.message.from_user:
        return False

    chat = update.effective_chat
    user = update.message.from_user
    try:
        member = await chat.get_member(user.id)
        # Check if user is admin or creator
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False
    
# Admin commands
async def warn_command(update, context):
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ Only group admins can use this command.")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to a user's message to warn them")
        return

    target_user = update.message.reply_to_message.from_user

    if await is_admin(update) or target_user.is_bot:
        await update.message.reply_text("❌ Cannot warn admins or bots")
        return

    user_warnings[target_user.id] = user_warnings.get(target_user.id, 0) + 1
    warnings_count = user_warnings[target_user.id]

    if warnings_count >= MAX_WARNINGS:
        await context.bot.ban_chat_member(update.effective_chat.id, target_user.id)
        await update.message.reply_text(f"🚫 Banned {target_user.first_name} for exceeding warnings")
        del user_warnings[target_user.id]
    else:
        await update.message.reply_text(
            f"⚠️ {target_user.first_name} has been warned ({warnings_count}/{MAX_WARNINGS})"
        )

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ Only group admins can use this command.")
        return

    target_user = update.message.reply_to_message.from_user

    if await is_admin(update) or target_user.is_bot:
        await update.message.reply_text("❌ Cannot ban admins or bots")
        return

    await context.bot.ban_chat_member(update.effective_chat.id, target_user.id)
    await update.message.reply_text(f"🚫 Banned {target_user.first_name}")
    user_warnings.pop(target_user.id, None)

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❌ Usage: /unban <user_id>")
        return

    try:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"✅ Unbanned user {user_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(welcome, chat_member_types=ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(ChatMemberHandler(goodbye, chat_member_types=ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_links))
    application.add_handler(CommandHandler("warn", warn_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_error_handler(error_handler)

    application.run_polling()
    
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)


if __name__ == "__main__":
    main()