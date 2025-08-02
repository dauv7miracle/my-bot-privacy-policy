import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameNotOccupied
from pyrogram.enums import ChatType

api_id = 22877754
api_hash = "e3810a342b4d893b50c6f2f1a8b31e0b" # I N S E R T  H E R E
app = Client("ubj1", api_id=api_id, api_hash=api_hash)

# 🧾 Command menu
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

def read_usernames():
    """Read usernames from text file, return as list"""
    # Use os.path to check file existence
    file_path = os.path.join(os.getcwd(), "usernames.txt")
    
    if not os.path.exists(file_path):
        # Create file if it doesn't exist
        with open(file_path, "w") as f:
            pass  # Create empty file
        return []
    
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_usernames(usernames):
    """Save usernames to text file"""
    file_path = os.path.join(os.getcwd(), "usernames.txt")
    with open(file_path, "w") as f:
        for username in usernames:
            f.write(f"{username}\n")

@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping(client, message: Message):
        print("Ping command received")
        await message.reply("Pong!")
    

# BROADCAST TO GROUPS
@app.on_message(filters.command("bc1b", prefixes=".") & filters.reply & filters.me)
async def broadcast_to_groups(client: Client, message: Message):
    target_message = message.reply_to_message

    if not target_message:
        await message.reply("❗Please reply to the message you want to broadcast.")
        return

    sent, failed = 0, 0
    failure_log = []

    try:
        with open("blacklisted_groups.txt", "r") as file:
            blacklisted_ids = set(map(int, file.read().splitlines()))
    except FileNotFoundError:
        blacklisted_ids = set()

    await message.reply("📢 Broadcasting to groups...")

    dialogs = []
    async for dialog in client.get_dialogs():
        dialogs.append(dialog)

    for dialog in dialogs:
        chat = dialog.chat
        if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            if chat.id in blacklisted_ids:
                print(f"🚫 Skipped blacklisted group: {chat.title} ({chat.id})")
                continue
            try:
                await target_message.forward(chat_id=chat.id)
                print(f"✅ Forwarded to group: {chat.title} ({chat.id})")
                sent += 1
                await asyncio.sleep(1.2)
            except Exception as e:
                error_reason = str(e)
                failed += 1
                group_title = chat.title or f"Unnamed Group {chat.id}"
                log_line = f"{group_title} ({chat.id}) - {error_reason}"
                print(f"❌ {log_line}")
                failure_log.append(log_line)
                await asyncio.sleep(0.5)

    # Save failure log
    log_path = os.path.join(os.getcwd(), "group_broadcast_failures.txt")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            if failure_log:
                f.write("\n".join(failure_log))
            else:
                f.write("No failures recorded.\n")
        print(f"📄 Log saved to: {log_path}")
    except Exception as e:
        print(f"❌ Failed to write log file: {e}")

    await message.reply(
        f"📤 Done!\nSent: {sent} ✅\nFailed: {failed} ❌" +
        ("\n\n🔻 Log written to 'group_broadcast_failures.txt'" if failed else "")
    )
    await send_command_menu(message)


# 🚫 Blacklist current group
@app.on_message(filters.command("addbl1", prefixes=".") & filters.me)
async def blacklist_group(client: Client, message: Message):
    dialogs = []
    async for dialog in client.get_dialogs():
        dialogs.append(dialog)
        for dialog in dialogs:
            chat = dialog.chat
            if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await message.reply("⚠️ This command must be used in a group.")
        return

    try:
        with open("blacklisted_groups.txt", "a+") as file:
            file.seek(0)
            blacklisted = file.read().splitlines()
            if str(chat.id) not in blacklisted:
                file.write(f"{chat.id}\n")
                await message.reply(f"🚫 Group '{chat.title}' has been blacklisted.")
            else:
                await message.reply("✅ This group is already blacklisted.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    await send_command_menu(message)


# ✅ Unblacklist current group
@app.on_message(filters.command("unbl1", prefixes=".") & filters.me)
async def unblacklist_group(client, message: Message):
    chat = message.chat
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("⚠️ This command must be used in a group.")
        return

    try:
        with open("blacklisted_groups.txt", "r") as file:
            groups = file.read().splitlines()

        if str(chat.id) in groups:
            groups.remove(str(chat.id))
            with open("blacklisted_groups.txt", "w") as file:
                file.write("\n".join(groups) + "\n")
            await message.reply(f"✅ Group '{chat.title}' has been unblacklisted.")
        else:
            await message.reply("ℹ️ This group is not blacklisted.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    await send_command_menu(message)


# 🧾 List blacklisted groups
@app.on_message(filters.command("bl_list1a", prefixes=".") & filters.me)
async def list_blacklisted_groups(client, message: Message):
    try:
        with open("blacklisted_groups.txt", "r") as file:
            groups = file.read().splitlines()

        if not groups:
            await message.reply("✅ No groups are currently blacklisted.")
            return

        text = "🚫 *Blacklisted Group IDs:*\n" + "\n".join(groups)
        await message.reply(text, quote=True)
    except FileNotFoundError:
        await message.reply("✅ No blacklist file found. You're all clear.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    await send_command_menu(message)


# 🧹 Clear all blacklisted groups
@app.on_message(filters.command("clear1a", prefixes=".") & filters.me)
async def clear_blacklisted_groups(client, message: Message):
    try:
        open("blacklisted_groups.txt", "w").close()
        await message.reply("🧹 All blacklisted groups have been cleared.")
    except Exception as e:
        await message.reply(f"❌ Error clearing blacklist: {e}")
    await send_command_menu(message)


# 📋 List contacts
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
        contact_lines.append(f"{name} | {username} | ID: `{user.id}`")

    chunk = ""
    for line in contact_lines:
        if len(chunk) + len(line) + 1 > 4000:
            await message.reply(chunk)
            chunk = ""
        chunk += line + "\n"

    if chunk:
        await message.reply(chunk)
    await send_command_menu(message)


# ℹ️ Help command
@app.on_message(filters.command("help1a", prefixes=".") & filters.me)
async def show_help(client, message: Message):
    help_text = """
📖 *Available Commands*:

👥 **Broadcasting**
• `.bc1a` — Broadcast message to all contacts (must reply to a message)
• `.bc1b` — Broadcast message to all groups (except blacklisted ones)

📌 **Contact Management**
• `.list1a` — List all saved contacts

🚫 **Group Blacklist Management**
• `.addbl1` — Blacklist the current group (used inside group)
• `.unbl1` — Remove the current group from blacklist
• `.bl_list1a` — Show all blacklisted group IDs
• `.clear1a` — Clear the entire group blacklist

❓ **Help**
• `.help1a` — Show this help message
"""
    await message.reply(help_text)

# 🧹 Clean up unsupported Groups
@app.on_message(filters.command("clean1a", prefixes=".") & filters.me)
async def clean_invalid_peers(client, message):
    removed, failed, checked = 0, 0, 0
    await message.reply("🔍 Scanning for invalid/broken chats...")

    async for dialog in client.get_dialogs():
        checked += 1
        try:
            chat = await client.get_chat(dialog.chat.id)
            # If get_chat works, the peer is valid
        except ValueError as e:
            if "Peer id invalid" in str(e):
                try:
                    await client.delete_chat(dialog.chat.id)
                    print(f"🗑️ Deleted invalid peer: {dialog.chat.id}")
                    removed += 1
                except Exception as ex:
                    print(f"❌ Failed to delete {dialog.chat.id}: {ex}")
                    failed += 1
        except Exception as ex:
            print(f"⚠️ Other error on {dialog.chat.id}: {ex}")
            failed += 1

    await message.reply(
        f"✅ Scan Complete\n\n"
        f"Total Dialogs Checked: {checked}\n"
        f"🗑️ Invalid Peers Removed: {removed}\n"
        f"❌ Errors: {failed}"
    )


user_waiting_for_broadcast = {}
# 📢 Broadcast to contacts
@app.on_message(filters.command("bc1a", prefixes=".") & filters.me & filters.private)
async def send_to_all_command(client: Client, message: Message):
    # Get the message you replied to
    target = message.reply_to_message
    if not target:
        await message.reply("❗ Please reply to the message you want to broadcast.")
        return

    usernames = read_usernames()
    if not usernames:
        await message.reply("❗ No usernames found in `usernames.txt`.")
        return

    await message.reply(f"📤 Starting broadcast to {len(usernames)} users...")

    success = 0
    failed = []

    for username in usernames:
        try:
    # Use `.forward()` to retain formatting/media/captions
            await target.forward(chat_id=username)
            success += 10
            await asyncio.sleep(1.1)
        except Exception as e:
            failed.append(f"{username}: {e}")

    result = (
        f"✅ Broadcast completed!\n\n"
        f"📬 Success: {success}\n"
        f"❌ Failed: {len(failed)}"
    )

    if failed:
        result += "\n\n🔻 Failed usernames:\n" + "\n".join(failed[:10])
        if len(failed) > 10:
            result += f"\n...and {len(failed)-10} more."

    await message.reply(result)
    await send_command_menu(message)

# ✅ Run the app
print("✅ Userbot is running. Waiting for commands...")
app.run()
