from pyrogram import Client
from pyrogram import filters

api_id = 20393163
api_hash = "9745c39c435457580d185295b8d08ecd"

app = Client("aa3", api_id=api_id, api_hash=api_hash)

@app.on_message(filters.command("list_chats", prefixes=".") & filters.me)
async def list_chats(client, message):
    text = ""
    async for dialog in client.get_dialogs():
        chat = dialog.chat
        text += f"{chat.title} ({chat.id}) — {chat.type}\n"
    await message.reply(text or "No chats found.")

app.run()
