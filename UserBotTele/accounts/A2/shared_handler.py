from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait
import os, asyncio, random

# 📜 Command Menu
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
        "`.clear1a` – Clear all blacklisted groups\n"
    )
    await message.reply(text)

# 📄 Utility functions
def read_usernames():
    file_path = os.path.join(os.getcwd(), "01usernames.txt")
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_usernames(usernames):
    file_path = os.path.join(os.getcwd(), "01usernames.txt")
    with open(file_path, "w") as f:
        for username in usernames:
            f.write(f"{username}\n")

# 🔁 Shared Handlers
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

        blacklist_file = "blacklisted_groups.txt"
        try:
            with open(blacklist_file, "r") as file:
                blacklisted_ids = set(map(int, file.read().splitlines()))
        except FileNotFoundError:
            blacklisted_ids = set()

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
                    # Use a small, randomized delay to appear more human
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                except FloodWait as e:
                    await status_msg.edit(f"FloodWait for {e.value}s. Sleeping...")
                    await asyncio.sleep(e.value + 5) # Wait for the duration of the floodwait + a buffer
                    failed += 1
                    failure_log.append(f"{chat.title or chat.id}: FloodWait for {e.value}s")
                except Exception as e:
                    failed += 1
                    error_reason = str(e)
                    failure_log.append(f"{chat.title or chat.id}: {error_reason}")
                    await asyncio.sleep(random.uniform(0.5, 1.0))

        result_text = f"📤 Broadcast Complete!\n\nSent: {sent} ✅\nFailed: {failed} ❌\nTotal Groups: {total_groups}"
        if failure_log:
            result_text += "\n\n**Failures:**\n" + "\n".join(failure_log[:10])

        await status_msg.edit(result_text)
        await send_command_menu(message)

    @app.on_message(filters.command("addbl1", prefixes=".") & filters.me)
    async def blacklist_group(client, message: Message):
        chat = message.chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await message.reply("⚠️ This command must be used in a group.")
            return

        blacklist_file = "blacklisted_groups.txt"
        with open(blacklist_file, "a+") as file:
            file.seek(0)
            blacklisted = file.read().splitlines()
            if str(chat.id) not in blacklisted:
                file.write(f"{chat.id}\n")
                await message.reply(f"🚫 Group '{chat.title}' has been blacklisted.")
            else:
                await message.reply("✅ This group is already blacklisted.")
        await send_command_menu(message)

    @app.on_message(filters.command("unbl1", prefixes=".") & filters.me)
    async def unblacklist_group(client, message: Message):
        chat = message.chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await message.reply("⚠️ This command must be used in a group.")
            return

        blacklist_file = "blacklisted_groups.txt"
        try:
            if not os.path.exists(blacklist_file):
                await message.reply("ℹ️ This group is not blacklisted (blacklist file does not exist).")
                return

            with open(blacklist_file, "r") as file:
                groups = file.read().splitlines()

            if str(chat.id) in groups:
                groups.remove(str(chat.id))
                with open(blacklist_file, "w") as file:
                    file.write("\n".join(groups) + "\n")
                await message.reply(f"✅ Group '{chat.title}' has been unblacklisted.")
            else:
                await message.reply("ℹ️ This group is not blacklisted.")
        except IOError as e:
            await message.reply(f"❌ Error: {e}")
        await send_command_menu(message)

    @app.on_message(filters.command("bl_list1a", prefixes=".") & filters.me)
    async def list_blacklisted_groups(client, message: Message):
        try:
            with open("blacklisted_groups.txt", "r") as file:
                groups = [g for g in file.read().splitlines() if g]
            if not groups:
                await message.reply("✅ No groups are currently blacklisted.")
            else:
                text = "🚫 *Blacklisted Group IDs:*\n" + "\n".join(f"`{g}`" for g in groups)
                await message.reply(text)
        except FileNotFoundError:
            await message.reply("✅ No blacklist file found. You're all clear.")
        await send_command_menu(message)

    @app.on_message(filters.command("clear1a", prefixes=".") & filters.me)
    async def clear_blacklisted_groups(client, message: Message):
        try:
            open("blacklisted_groups.txt", "w").close()
            await message.reply("🧹 All blacklisted groups have been cleared.")
        except Exception as e:
            await message.reply(f"❌ Error clearing blacklist: {e}")
        await send_command_menu(message)

    @app.on_message(filters.command("list1a", prefixes=".") & filters.me)
    async def list_contacts(client, message: Message):
        contacts = await client.get_contacts()
        if not contacts:
            await message.reply("❗ You have no saved contacts.")
            return

        contact_lines = []
        for user in contacts:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "(no username)"
            contact_lines.append(f"• {name} | {username} | ID: `{user.id}`")

        response_chunk = "📋 **Your Contacts:**\n\n"
        for line in contact_lines:
            if len(response_chunk) + len(line) + 1 > 4096:
                await message.reply(response_chunk, quote=True)
                response_chunk = ""
            response_chunk += line + "\n"

        if response_chunk:
            await message.reply(response_chunk, quote=True)
        await send_command_menu(message)

    @app.on_message(filters.command("help1a", prefixes=".") & filters.me)
    async def show_help(client, message: Message):
        await send_command_menu(message)

    @app.on_message(filters.command("clean1a", prefixes=".") & filters.me)
    async def clean_invalid_peers(client, message):
        removed, failed, checked = 0, 0, 0
        await message.reply("🔍 Scanning for invalid/broken chats...")
        async for dialog in client.get_dialogs():
            checked += 1
            try:
                await client.get_chat(dialog.chat.id)
            except ValueError as e:
                if "Peer id invalid" in str(e).lower():
                    try:
                        await client.delete_chat(dialog.chat.id)
                        removed += 1
                    except Exception as ex:
                        print(f"Failed to delete invalid chat {dialog.chat.id}: {ex}")
                        failed += 1
            except Exception as e:
                print(f"Error checking chat {dialog.chat.id}: {e}")
                failed += 1
        await message.reply(f"✅ Scan Complete\nChecked: {checked}\nRemoved: {removed}\nFailed: {failed}")

    @app.on_message(filters.command("bc1a", prefixes=".") & filters.reply & filters.me)
    async def send_to_all_command(client, message: Message):
        quantity = None
        if len(message.command) > 1:
            try:
                quantity = min(500, int(message.command[1].lstrip('!')))
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
        total = len(all_usernames)
        quantity = quantity or total
        batch = all_usernames[:quantity]
        remaining_usernames = all_usernames[quantity:]
        success_count, failed_count = 0, 0
        failed_log = []

        status = await message.reply(f"📤 Broadcasting to {len(batch)} of {total} users...")

        for i, username in enumerate(batch):
            try:
                await target.forward(chat_id=username)
                success_count += 1
            except Exception as e:
                failed_count += 1
                failed_log.append(f"{username}: {str(e)}")

            # Update status message periodically
            if (i + 1) % 10 == 0 or (i + 1) == len(batch):
                await status.edit_text(
                    f"📤 Broadcasting... {i+1}/{len(batch)}\n"
                    f"✅ Success: {success_count} | ❌ Failed: {failed_count}"
                )
            print("📥 Received .bc1a command")

            if i < len(batch) - 1:
                await asyncio.sleep(random.uniform(5, 10))

        save_usernames(remaining_usernames)
        await status.delete()
        await message.reply(f"✅ Broadcast Complete!\n\nSent: {success_count}\nFailed: {failed_count}\nRemaining: {len(remaining_usernames)}")
        await send_command_menu(message)
