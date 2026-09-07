import asyncio
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins

scratch_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"
session_path = os.path.join(scratch_dir, "jinli072_userbot")
API_ID = 39866164
API_HASH = "c0612f0ffb574a44f51f496191ef6453"

async def check_admins():
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    gid = -1004328184189
    entity = await client.get_entity(gid)
    me = await client.get_me()
    print(f"Checking admins for: {entity.title} ({entity.id})")
    async for user in client.iter_participants(entity, filter=ChannelParticipantsAdmins):
        is_me = (user.id == me.id)
        print(f"Admin: {user.id} - {user.first_name} {user.last_name or ''} (@{user.username}) {'[ME]' if is_me else ''}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_admins())
