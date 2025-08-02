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
        "name": "26j1",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j2",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j3",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j4",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j5",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j6",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j7",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j8",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j9",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j10",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j11",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j12",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j13",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j14",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j15",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j16",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j17",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j18",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j19",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j20",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j21",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j22",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j23",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j24",
        "api_id": 23011951,
        "api_hash": "a9669e04a2c06c5461574d4170272911"
    },
    {
        "name": "26j25",
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