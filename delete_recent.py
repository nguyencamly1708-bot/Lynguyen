import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from telethon import TelegramClient

scratch_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"
session_path = os.path.join(scratch_dir, "jinli072_userbot")

API_ID = 39866164
API_HASH = "c0612f0ffb574a44f51f496191ef6453"

async def fast_delete():
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("Not authorized", flush=True)
        return

    me = await client.get_me()
    print(f"Connected as {me.id} ({me.first_name})", flush=True)

    # We want to delete any messages sent in the last 2 hours (after 06:30 UTC / 13:30 local)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
    deleted_total = 0

    print("Quick scanning all dialogs by last message timestamp...", flush=True)
    async for dialog in client.iter_dialogs(limit=None):
        # If dialog has no message or last message is older than cutoff, skip!
        last_msg = dialog.message
        if not last_msg:
            continue
            
        # Is it A131 specifically or any recent active dialog?
        is_target_name = "131" in (dialog.name or "") or "A131" in (dialog.name or "")
        
        if last_msg.date >= cutoff or is_target_name:
            # Check last 10 messages in this dialog
            to_del = []
            try:
                async for msg in client.iter_messages(dialog, limit=10):
                    if msg.date >= cutoff:
                        if msg.out or msg.sender_id == me.id:
                            to_del.append(msg.id)
                            txt = (msg.text or "")[:40].replace("\n", " ")
                            print(f"  [Found] in '{dialog.name}' msg {msg.id} ({msg.date}): {txt}", flush=True)
                if to_del:
                    await client.delete_messages(dialog, to_del, revoke=True)
                    print(f"  ===> [DELETED FOR EVERYONE] {len(to_del)} messages in '{dialog.name}'!", flush=True)
                    deleted_total += len(to_del)
            except Exception as e:
                print(f"  Error in '{dialog.name}': {e}", flush=True)

    print(f"\n==========================================", flush=True)
    print(f"DONE! Deleted {deleted_total} messages for everyone!", flush=True)
    print(f"==========================================", flush=True)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(fast_delete())
