import json
import os
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ChatJoinRequestHandler, MessageHandler, filters
)
import urllib.parse
import asyncio
from database import get_db_connection, init_db
from dotenv import load_dotenv
import uuid
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('TELEGRAM_GROUP_ID', 0))
DATA_DIR = 'data'

# Constants
INVITE_LINK_EXPIRY = 600  # seconds (10 minutes)
LINK_CLEANUP_AGE = 86400  # seconds (1 day)
CLAIM_THRESHOLD = 20
# File paths
INVITE_MAPPING_FILE = os.path.join(DATA_DIR, 'invite_mapping.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_invite_mapping():
    if os.path.exists(INVITE_MAPPING_FILE):
        try:
            with open(INVITE_MAPPING_FILE, 'r') as f:
                data = json.load(f)
                # Filter out malformed entries
                return {k: v for k, v in data.items() if isinstance(v, dict)}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_invite_mapping(data):
    with open(INVITE_MAPPING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def store_invite_mapping(unique_id, invite_link, inviter_id):
    data = load_invite_mapping()
    data[unique_id] = {
        'link': invite_link,
        'inviter': inviter_id,
        'created_at': int(time.time())
    }
    save_invite_mapping(data)

def get_invite_info_by_full_url(full_url):
    data = load_invite_mapping()
    for uid, info in data.items():
        if info['link'] == full_url:
            return uid, info['inviter']
    return None, None

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def record_referral_join(inviter_id, referred_id):
    """Records a referral join in the database and updates points."""
    with get_db_connection() as conn:
        cur = conn.cursor()

        # 1. Check if the referred user has already been processed
        cur.execute("SELECT user_id FROM processed_users WHERE user_id = ?", (referred_id,))
        if cur.fetchone():
            logger.warning(f"User {referred_id} has already been processed. Ignoring referral.")
            return False

        # 2. Add the new user to the processed list
        cur.execute(
            "INSERT INTO processed_users (user_id, source, inviter_id, timestamp) VALUES (?, ?, ?, ?)",
            (referred_id, 'referral_link', inviter_id, int(time.time()))
        )

        # 3. Update the inviter's points
        # Use INSERT OR IGNORE to create a row for the inviter if they don't exist
        cur.execute("INSERT OR IGNORE INTO user_points (user_id) VALUES (?)", (inviter_id,))
        # Atomically update the points
        cur.execute(
            """
            UPDATE user_points
            SET referral_links = referral_links + 1, total = total + 1
            WHERE user_id = ?
            """,
            (inviter_id,)
        )
        conn.commit()
        logger.info(f"Successfully recorded referral: inviter {inviter_id}, referred {referred_id}")
        return True

async def delete_after_delay(context, chat_id, message_id, delay):
    """Delete a message after a specified delay"""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.debug(f"Deleted message {message_id} in chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

async def auto_delete_response(update: Update, context: ContextTypes.DEFAULT_TYPE, response_text: str):
    """Send a response and schedule it for deletion"""
    sent = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )
    
    # Schedule deletion
    asyncio.create_task(delete_after_delay(context, sent.chat_id, sent.message_id, 100))
    
    # Delete user's command if in group
    if update.message and update.message.chat.type in ["group", "supergroup"]:
        try:
            await context.bot.delete_message(
                chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
        except Exception as e:
            logger.error(f"Failed to delete user command: {e}")

async def clean_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete service messages (join/leave notifications)"""
    try:
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        logger.info(f"Deleted service message: {update.message.message_id}")
    except Exception as e:
        logger.error(f"Failed to delete service message: {e}")

async def create_invite_link(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        bot = context.bot
        invite_link = await bot.create_chat_invite_link(
            chat_id=GROUP_ID,
            expire_date=int(time.time()) + INVITE_LINK_EXPIRY,  # 10-minute expiry
            creates_join_request=True,
            name=f"ref_{user_id}"
        )
        return invite_link.invite_link
    except Exception as e:
        logger.error(f"Error creating invite link: {e}")
        return None

async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    try:
        invite_link = await create_invite_link(context, user_id)
        if not invite_link:
            await auto_delete_response(update, context, "⚠️ Failed to create invite link. Please try again later.")
            return
            
        unique_id = str(uuid.uuid4())
        store_invite_mapping(unique_id, invite_link, user_id)

        # Embed UUID into share URL
        share_url = (
            f"https://t.me/share/url?"
            + f"url={urllib.parse.quote_plus(invite_link)}"
            + f"&text=Join%20Now!&ref={unique_id}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Share Now", url=share_url)]
        ])

        sent = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Hi {user.first_name}! 🎉\n\n"
                f"Free Credit link:\n<code>{invite_link}</code>\n\n"
                "Share this link to earn FREE CREDIT RM5!"
            ),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        asyncio.create_task(delete_after_delay(context, sent.chat_id, sent.message_id, 100))
    except Exception as e:
        logger.error(f"Error in share command: {e}", exc_info=True)
        await auto_delete_response(update, context, "⚠️ Failed to create invite link. Please try again later.")

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)
    points_info = {'referral_links': 0, 'manual_adds': 0, 'total': 0}

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT referral_links, manual_adds, total FROM user_points WHERE user_id = ?", (user.id,))
            row = cur.fetchone()
            if row:
                points_info = dict(row)
    except Exception as e:
        logger.error(f"Failed to fetch points for user {user.id}: {e}")

    await auto_delete_response(update, context,
        f"🏆 Your Points:\n\n"
        f"Referral Links: {points_info['referral_links']}\n"
        f"Manual Adds: {points_info['manual_adds']}\n"
        f"Total Points: {points_info['total']}"
    )

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Check points
            cur.execute("SELECT total FROM user_points WHERE user_id = ?", (user.id,))
            row = cur.fetchone()
            if not row or row['total'] < CLAIM_THRESHOLD:
                needed = CLAIM_THRESHOLD - (row['total'] if row else 0)
                await auto_delete_response(update, context, f"⚠️ You need {needed} more points to claim a reward!")
                return

            # Deduct points
            cur.execute("UPDATE user_points SET total = total - ? WHERE user_id = ?", (CLAIM_THRESHOLD, user.id))
            conn.commit()

            if cur.rowcount == 0: # Should not happen if check passed, but good for safety
                logger.warning(f"Failed to deduct points for {user.id} during claim.")
                return
    except Exception as e:
        logger.error(f"Error during claim process for {user.id}: {e}")
        await auto_delete_response(update, context, "⚠️ An error occurred during the claim process. Please try again.")
        return
    
    # Send announcement and schedule deletion
    sent = await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"🎉 Congratulations! {user.mention_html()} can claim RM5! Chat @RMGROUP76 to receive your Free Credit!!",
        parse_mode='HTML'
    )
    asyncio.create_task(delete_after_delay(context, sent.chat_id, sent.message_id, 60))

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user_id = str(request.from_user.id)
    user_name = request.from_user.full_name
    
    # Get the invite link as string
    full_link = request.invite_link.invite_link if request.invite_link else None
    
    if not full_link:
        # User joined through non-tracked method (admin invitation, direct link, etc)
        logger.info(f"Approved join for {user_name} (ID: {user_id}) via non-tracked method")
        try:
            await context.bot.approve_chat_join_request(
                chat_id=request.chat.id, 
                user_id=request.from_user.id
            )
        except Exception as e:
            logger.error(f"Failed to approve join request: {e}")
        return

    logger.info(f"{user_name} (ID: {user_id}) joined via link: {full_link}")

    # Get inviter ID from mapping
    uid, inviter_id = get_invite_info_by_full_url(full_link)
    if inviter_id:
        logger.info(f"Matched invite to inviter: {inviter_id}")
        
        # Record referral using actual inviter ID
        if record_referral_join(inviter_id, user_id):
            logger.info(f"Points updated for inviter {inviter_id} via referral join.")
    else:
        logger.warning(f"No matching invite found for link: {full_link}. Could be an expired or admin-created link.")

    # Always approve the request
    try:
        await context.bot.approve_chat_join_request(
            chat_id=request.chat.id, 
            user_id=request.from_user.id
        )
    except Exception as e:
        logger.error(f"Failed to approve join request: {e}")

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # The service message ("User joined") is now reliably deleted by the userbot (ubot.py)
    # to avoid race conditions. This function will now only send the welcome message.
    logger.info(f"Sending welcome message for new member(s) in chat {update.message.chat_id}")

    bot_username = context.bot.username
    deep_link = f"https://t.me/{bot_username}?start=share"

    for member in update.message.new_chat_members:
        # Skip if it's the bot itself
        if member.id == context.bot.id:
            continue
            
        welcome_text = (
            f"👋 Welcome {member.mention_html()} 🎉\n\n"
            "🎁 Claim FREE CREDIT RM5 by inviting 20 friends:\n"
            "Click the button below to start!"
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📝 FREE CREDIT RM5", url=deep_link)
        ]])
        try:
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            asyncio.create_task(delete_after_delay(context, msg.chat_id, msg.message_id, 60))
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

async def send_welcome(update, context, new_members):
    try:
        chat = await context.bot.get_chat(update.effective_chat.id)
        perms = chat.permissions
        logger.info(f"Chat permissions: {perms.to_dict()}")
    except:
        logger.warning("Couldn't fetch chat permissions")
    # ... rest of code ...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and args[0] == 'share':
        await share(update, context)
    else:
        await update.message.reply_text(
            "👋 Welcome!\n\n"
            "Use /share to get your referral link and earn free credit!\n"
            "Use /points to check your points.\n"
            "Use /claim to redeem your points for rewards."
        )

async def cleanup_expired_links():
    """Periodically remove expired invite mappings"""
    while True:
        try:
            now = int(time.time())
            data = load_invite_mapping()
            expired = []
            
            for uid, info in list(data.items()):
                # Remove links older than 1 day (86400 seconds)
                if now - info.get('created_at', 0) > LINK_CLEANUP_AGE:
                    expired.append(uid)
            
            for uid in expired:
                del data[uid]
            
            if expired:
                save_invite_mapping(data)
                logger.info(f"Cleaned up {len(expired)} expired links")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        
        await asyncio.sleep(3600)


# Setup application
def main():
    # Initialize database and files
    init_db()
    if not os.path.exists(INVITE_MAPPING_FILE): save_json({}, INVITE_MAPPING_FILE)
    
    app = ApplicationBuilder().token(TOKEN).build()
    

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("share", share))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Add service message cleaner
    app.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER,
        clean_service_messages
    ))
    
    # Add handler for new members
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        new_member
    ))
    
    # Start cleanup task
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_expired_links())
    
    logger.info("Referral bot is running with improved invite tracking...")
    app.run_polling()

if __name__ == '__main__':
    main()
