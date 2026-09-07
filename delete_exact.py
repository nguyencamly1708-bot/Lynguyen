import asyncio
import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from telethon import TelegramClient

scratch_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"
session_path = os.path.join(scratch_dir, "jinli072_userbot")

API_ID = 39866164
API_HASH = "c0612f0ffb574a44f51f496191ef6453"

async def delete_exact():
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("Not authorized", flush=True)
        return

    me = await client.get_me()
    print(f"Connected as {me.id} ({me.first_name})", flush=True)
    
    deleted_count = 0
    scanned_groups = 0

    print("Searching ONLY in GROUPS/CHANNELS for 'Ly gửi DS phiếu đổi trả' or 'Phiếu chuyển/PGH'...", flush=True)
    async for dialog in client.iter_dialogs(limit=None):
        if not (dialog.is_group or dialog.is_channel):
            continue
        scanned_groups += 1
        try:
            to_del = []
            async for msg in client.iter_messages(dialog, limit=10):
                txt = msg.text or ""
                if "phiếu đổi trả" in txt.lower() or "chưa nhận được chứng từ" in txt.lower() or "phiếu chuyển/pgh" in txt.lower():
                    to_del.append(msg.id)
                    print(f"MATCH: Group '{dialog.name}' (ID: {dialog.id}), Msg ID: {msg.id}, Date: {msg.date}", flush=True)
            if to_del:
                await client.delete_messages(dialog, to_del, revoke=True)
                print(f"===> SUCCESS: Deleted {len(to_del)} messages in '{dialog.name}' FOR EVERYONE!", flush=True)
                deleted_count += len(to_del)
        except Exception as e:
            pass

    print(f"\n==========================================", flush=True)
    print(f"DONE: Scanned {scanned_groups} groups. Deleted {deleted_count} messages for everyone!", flush=True)
    print(f"==========================================", flush=True)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(delete_exact())
