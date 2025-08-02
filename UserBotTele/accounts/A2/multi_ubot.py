# multi_userbot.py
import asyncio
import os
from pyrogram import Client
from shared_handler import register_handlers

# Create session folder if it doesn't exist
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

userbots = [
    {
        "name": "ang1",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang2",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang3",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang4",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang5",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang6",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang7",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang8",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang9",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang10",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang11",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang12",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang13",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang14",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang15",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang16",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang17",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "ang18",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    
    # Add more bots here
]

clients = []

async def main():
    stop_event = asyncio.Event()

    for bot in userbots:
        session_path = os.path.join(SESSION_DIR, bot["name"])
        client = Client(name=session_path, api_id=bot["api_id"], api_hash=bot["api_hash"])
        await client.start()
        register_handlers(client)
        clients.append(client)

    print("✅ All userbots started")

    try:
        await stop_event.wait()  # Keeps running
    except KeyboardInterrupt:
        print("🛑 Stopping all userbots...")
    finally:
        for client in clients:
            await client.stop()

asyncio.run(main())