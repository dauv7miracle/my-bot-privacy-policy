import asyncio
import json
import os
import logging
import sqlite3
from dotenv import load_dotenv
from telethon import TelegramClient, events
import time
from telethon.tl.types import MessageService, PeerUser
from telethon.utils import get_display_name
from database import get_db_connection, init_db # Import from shared database file

# Load environment variables from .env file
load_dotenv()  # Add this

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Userbot configuration
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = 'ashley'
GROUP_ID = -1001994897952
DATA_DIR = 'data'
LOCK_TIMEOUT = 10
DB_FILE = os.path.join(DATA_DIR, 'bot_data.db')

# File paths
os.makedirs(DATA_DIR, exist_ok=True)

def record_manual_add(adder_id, added_id):
    """Records a manual add in the database. Returns True if successful, False otherwise."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # 1. Check if the added user has already been processed
            cur.execute("SELECT user_id FROM processed_users WHERE user_id = ?", (added_id,))
            if cur.fetchone():
                logger.warning(f"User {added_id} was already processed. Skipping manual add record.")
                return False

            # 2. Add the new user to the processed list
            cur.execute(
                "INSERT INTO processed_users (user_id, source, inviter_id, timestamp) VALUES (?, ?, ?, ?)",
                (added_id, 'manual_add', adder_id, int(time.time()))
            )
            
            # 3. Update the adder's points
            # Use INSERT OR IGNORE to create a row for the adder if they don't exist
            cur.execute("INSERT OR IGNORE INTO user_points (user_id) VALUES (?)", (adder_id,))
            # Atomically update the points
            cur.execute(
                """
                UPDATE user_points
                SET manual_adds = manual_adds + 1, total = total + 1
                WHERE user_id = ?
                """,
                (adder_id,)
            )
            conn.commit()
            logger.info(f"Successfully recorded manual add: adder {adder_id}, added {added_id}")
            return True
    except Exception as e:
        logger.error(f"Database error in record_manual_add for adder {adder_id}: {e}", exc_info=True)
        return False

async def delete_message_after_delay(client, message, delay):
    """Delete a message after a specified delay"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
        logger.debug(f"Deleted message {message.id}")
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")

async def main():
    if not API_ID or not API_HASH:
        logger.error("API_ID or API_HASH is missing! Please set environment variables.")
        return

    # Ensure the database is initialized, just in case this bot starts first
    init_db()
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    try:
        await client.start()
        logger.info("Userbot started successfully!")
    except Exception as e:
        logger.error(f"Failed to start userbot: {e}")
        return
    
    try:
        group = await client.get_entity(GROUP_ID)
    except Exception as e:
        logger.error(f"Failed to get group: {e}")
        return

    # 🟩 1. Delete all user commands (e.g. /start, /help, etc.)
    @client.on(events.NewMessage(chats=group.id, pattern=r'^/'))
    async def handle_command(event):
        try:
            await event.delete()
            logger.info(f"Deleted user command: {event.text}")
        except Exception as e:
            logger.error(f"Failed to delete command: {e}")

    # 🟩 2. Delete all messages sent by the bot after 10 seconds
    @client.on(events.NewMessage(outgoing=True, chats=group.id))
    async def auto_delete_bot_message(event):
        # Don't delete service messages
        if not isinstance(event.message, MessageService):
            await delete_message_after_delay(client, event.message, delay=10)

    # 🟩 3. Track manual member additions & delete service message
    @client.on(events.ChatAction(chats=group.id))
    async def handle_chat_action(event):
        # Delete the service message immediately
        if event.action_message:
            try:
                await event.action_message.delete()
                logger.info("Deleted service message (join/leave)")
            except Exception as e:
                logger.error(f"Failed to delete service message: {e}")
        
        # Handle bulk adds
        if event.user_added:
            adder_id = None
            
            # Get adder from the action message
            if event.action_message and event.action_message.from_id:
                if isinstance(event.action_message.from_id, PeerUser):
                    adder_id = event.action_message.from_id.user_id
            
            # If no adder in action message, use the action user
            if adder_id is None and event.user_id:
                adder_id = event.user_id
            
            if adder_id is None:
                logger.warning("Could not determine adder for new members")
                return
            
            # Process all added users
            added_count = 0
            for added_user in event.users:
                try:
                    # The record_manual_add function now handles point updates directly
                    if record_manual_add(adder_id, added_user.id):
                        added_count += 1
                except Exception as e:
                    logger.error(f"Error recording add for user {added_user.id}: {e}")
            
            # Notify only if we added at least one user
            if added_count > 0:
                try:
                    adder_name = get_display_name(await client.get_entity(adder_id))
                    msg_text = f"🎉 {adder_name} earned {added_count} point(s) for adding {added_count} new member(s)!"
                    
                    msg = await client.send_message(
                        group.id,
                        msg_text
                    )
                    await delete_message_after_delay(client, msg, delay=20)
                except Exception as e:
                    logger.error(f"Notification failed: {e}")
    
    logger.info("Monitoring group for joins, commands, and cleaning bot messages...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())