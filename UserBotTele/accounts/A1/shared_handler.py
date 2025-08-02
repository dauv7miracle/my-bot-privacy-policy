from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait
import os, asyncio, random

# Updated Command Menu
async def send_command_menu(message: Message):
    text = (
        "📜 *Available Commands:*\n\n"
        "👥 Contacts:\n"
        "`.bc1a` – Broadcast to contacts\n"
        "`.list1a` – List all saved contacts\n\n"
        "👥 Groups:\n"
        "`.bc1b` – Broadcast to groups\n"
        "`.addbl1` – Blacklist current group\n"
        "`.unbl1` – Unblacklist current group\n"
        "`.bl_list1a` – List all blacklisted groups\n"
        "`.clear1a` – Clear all blacklisted groups\n\n"
        "🌐 Group Joining:\n"
        "`.join1a` – Join groups from list\n"
    )
    await message.reply(text)

# Utility functions
def read_usernames():
    file_path = "01usernames.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_usernames(usernames):
    with open("01usernames.txt", "w") as f:
        for username in usernames:
            f.write(f"{username}\n")

def get_blacklisted_groups():
    blacklist_file = "blacklisted_groups.txt"
    if not os.path.exists(blacklist_file):
        return set()
    with open(blacklist_file, "r") as file:
        return set(map(int, file.read().splitlines()))

def save_blacklisted_groups(blacklisted_ids):
    with open("blacklisted_groups.txt", "w") as file:
        for chat_id in blacklisted_ids:
            file.write(f"{chat_id}\n")

# Main handlers
def register_handlers(app: Client):
    @app.on_message(filters.command("ping", prefixes=".") & filters.me)
    async def ping_handler(client, message):
        await message.reply_text("pong ✅")

    @app.on_message(filters.command("bc1b", prefixes=".") & filters.reply & filters.me)
    async def broadcast_to_groups(client: Client, message: Message):
        target_message = message.reply_to_message
        if not target_message:
            await message.reply("❗Please reply to the message you want to broadcast.")
            return

        blacklisted_ids = get_blacklisted_groups()
        status_msg = await message.reply("📢 Broadcasting to groups...")
        sent, failed, total_groups = 0, 0, 0
        failure_log = []

        async for dialog in client.get_dialogs():
            chat = dialog.chat
            if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                total_groups += 1
                if chat.id in blacklisted_ids:
                    continue

                try:
                    await target_message.forward(chat_id=chat.id)
                    sent += 1
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                except FloodWait as e:
                    await status_msg.edit(f"⏳ FloodWait: Sleeping for {e.value}s...")
                    await asyncio.sleep(e.value + 5)
                    failed += 1
                    failure_log.append(f"{chat.title or chat.id}: FloodWait {e.value}s")
                except Exception as e:
                    failed += 1
                    failure_log.append(f"{chat.title or chat.id}: {str(e)}")
                    await asyncio.sleep(0.5)

        result_text = f"📤 Broadcast Complete!\n\nSent: {sent} ✅\nFailed: {failed} ❌\nTotal Groups: {total_groups}"
        if failure_log:
            result_text += "\n\n**First 10 Failures:**\n" + "\n".join(failure_log[:10])
        
        await status_msg.edit(result_text)
        await send_command_menu(message)

    @app.on_message(filters.command("addbl1", prefixes=".") & filters.me)
    async def blacklist_group(client, message: Message):
        chat = message.chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await message.reply("⚠️ This command must be used in a group.")
            return

        blacklisted_ids = get_blacklisted_groups()
        if chat.id in blacklisted_ids:
            await message.reply("✅ This group is already blacklisted.")
            return
            
        blacklisted_ids.add(chat.id)
        save_blacklisted_groups(blacklisted_ids)
        await message.reply(f"🚫 Group '{chat.title}' has been blacklisted.")
        await send_command_menu(message)

    @app.on_message(filters.command("unbl1", prefixes=".") & filters.me)
    async def unblacklist_group(client, message: Message):
        chat = message.chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await message.reply("⚠️ This command must be used in a group.")
            return

        blacklisted_ids = get_blacklisted_groups()
        if not blacklisted_ids:
            await message.reply("ℹ️ No groups are blacklisted.")
            return

        if chat.id not in blacklisted_ids:
            await message.reply("ℹ️ This group is not blacklisted.")
            return
            
        blacklisted_ids.remove(chat.id)
        save_blacklisted_groups(blacklisted_ids)
        await message.reply(f"✅ Group '{chat.title}' has been unblacklisted.")
        await send_command_menu(message)

    @app.on_message(filters.command("bl_list1a", prefixes=".") & filters.me)
    async def list_blacklisted_groups(client, message: Message):
        blacklisted_ids = get_blacklisted_groups()
        if not blacklisted_ids:
            await message.reply("✅ No groups are currently blacklisted.")
            return
            
        text = "🚫 *Blacklisted Group IDs:*\n" + "\n".join(f"`{g}`" for g in blacklisted_ids)
        await message.reply(text)
        await send_command_menu(message)

    @app.on_message(filters.command("clear1a", prefixes=".") & filters.me)
    async def clear_blacklisted_groups(client, message: Message):
        if os.path.exists("blacklisted_groups.txt"):
            os.remove("blacklisted_groups.txt")
            await message.reply("🧹 All blacklisted groups have been cleared.")
        else:
            await message.reply("ℹ️ Blacklist file doesn't exist.")
        await send_command_menu(message)

    @app.on_message(filters.command("list1a", prefixes=".") & filters.me)
    async def list_contacts(client, message: Message):
        contacts = await client.get_contacts()
        if not contacts:
            await message.reply("❗ You have no saved contacts.")
            return

        response = []
        for user in contacts:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "No username"
            response.append(f"• {name} | {username} | ID: `{user.id}`")

        # Split into chunks of 40 contacts each
        for i in range(0, len(response), 40):
            chunk = response[i:i+40]
            await message.reply("📋 **Your Contacts:**\n\n" + "\n".join(chunk))
        
        await send_command_menu(message)

    @app.on_message(filters.command("help1a", prefixes=".") & filters.me)
    async def show_help(client, message: Message):
        await send_command_menu(message)

    @app.on_message(filters.command("clean1a", prefixes=".") & filters.me)
    async def clean_invalid_peers(client, message):
        await message.reply("🔍 Scanning for invalid chats...")
        removed, failed, checked = 0, 0, 0
        
        async for dialog in client.get_dialogs():
            checked += 1
            try:
                await client.get_chat(dialog.chat.id)
            except (ValueError, KeyError):
                try:
                    await client.delete_chat(dialog.chat.id)
                    removed += 1
                except Exception:
                    failed += 1
            except Exception:
                failed += 1
                
        await message.reply(f"✅ Scan Complete\nChecked: {checked}\nRemoved: {removed}\nFailed: {failed}")

    @app.on_message(filters.command("bc1a", prefixes=".") & filters.reply & filters.me)
    async def send_to_all_command(client, message: Message):
        quantity = 500  # Default limit
        if len(message.command) > 1:
            try:
                quantity = min(500, int(message.command[1]))
            except ValueError:
                pass
                
        target = message.reply_to_message
        if not target:
            await message.reply("❗ Reply to the message you want to broadcast.")
            return
            
        all_usernames = read_usernames()
        if not all_usernames:
            await message.reply("❗ No usernames in 01usernames.txt.")
            return
            
        batch = all_usernames[:quantity]
        remaining = all_usernames[quantity:]
        success, failed = 0, 0
        status = await message.reply(f"📤 Broadcasting to {len(batch)} users...")

        for i, username in enumerate(batch):
            try:
                await target.forward(username)
                success += 1
            except Exception as e:
                failed += 1
                
            # Update every 10 users
            if (i + 1) % 10 == 0:
                await status.edit(f"📤 Progress: {i+1}/{len(batch)}\n✅ {success} | ❌ {failed}")
                
            if i < len(batch) - 1:
                await asyncio.sleep(random.uniform(5, 10))

        save_usernames(remaining)
        await status.delete()
        await message.reply(f"✅ Broadcast Complete!\nSent: {success}\nFailed: {failed}\nRemaining: {len(remaining)}")
        await send_command_menu(message)

    @app.on_message(filters.command("join1a", prefixes=".") & filters.me)
    async def join_groups_command(client: Client, message: Message):
        """Join groups from groups_to_join.txt"""
        join_file = "groups_to_join.txt"
        if not os.path.exists(join_file):
            await message.reply(f"❌ File `{join_file}` not found.")
            return
        
    # Read with UTF-8 encoding to handle special characters
        with open(join_file, "r", encoding="utf-8") as f:
            group_links = [line.strip() for line in f if line.strip()]
        
        if not group_links:
            await message.reply(f"ℹ️ No group links in `{join_file}`")
            return
        
        status_msg = await message.reply(f"🚀 Joining {len(group_links)} groups...")
        success, failed = 0, 0
        results = []
    
        for i, link in enumerate(group_links):
            try:
                await client.join_chat(link)
                success += 1
                results.append(f"✅ {link}")
                await asyncio.sleep(random.uniform(3, 7))
            except FloodWait as e:
                await asyncio.sleep(e.value + 5)
                try:
                    await client.join_chat(link)
                    success += 1
                    results.append(f"✅ {link} (after FloodWait)")
                except Exception:
                    failed += 1
                    results.append(f"❌ {link} (FloodWait retry failed)")
            except Exception as e:
                failed += 1
                results.append(f"❌ {link}: {str(e)}")
            
            # Update every 10 groups
            if (i + 1) % 10 == 0:
                await status_msg.edit(f"⏳ {i+1}/{len(group_links)}\n✅ {success} | ❌ {failed}")
    
        # Save results with UTF-8 encoding
        with open("join_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        
        report = (
            f"🏁 Join Complete!\n"
            f"• Total: {len(group_links)}\n"
            f"• Success: {success} ✅\n"
            f"• Failed: {failed} ❌\n\n"
            f"Full results saved to `join_results.txt`"
        )
        
        await status_msg.delete()
        await message.reply(report, disable_web_page_preview=True)
        await send_command_menu(message)