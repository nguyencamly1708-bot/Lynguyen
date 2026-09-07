import asyncio
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from telethon import TelegramClient

scratch_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"
session_path = os.path.join(scratch_dir, "jinli072_userbot")
API_ID = 39866164
API_HASH = "c0612f0ffb574a44f51f496191ef6453"

async def check_a131():
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    gid = -5167161385
    entity = await client.get_entity(gid)
    print(f"Checking entity: {entity.title} (ID: {entity.id})")
    async for m in client.iter_messages(entity, limit=10):
        print(f"Msg ID: {m.id} | Date: {m.date} | Out: {m.out} | Sender: {m.sender_id} | Text: {(m.text or '')[:60]}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_a131())
