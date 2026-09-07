import asyncio
import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from telethon import TelegramClient
from telethon.tl.functions.channels import GetAdminLogRequest
from telethon.tl.types import ChannelAdminLogEventsFilter

scratch_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"
session_path = os.path.join(scratch_dir, "jinli072_userbot")

API_ID = 39866164
API_HASH = "c0612f0ffb574a44f51f496191ef6453"

async def check_admin_log():
    # Stop server temporarily if running or use userbot
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    
    # Check both groups
    group_ids = [-1004328184189, -5250588283]
    
    for gid in group_ids:
        print(f"\n--- Checking Group {gid} ---")
        try:
            entity = await client.get_entity(gid)
            print(f"Title: {entity.title} | Type: {type(entity).__name__}")
            
            # Fetch Admin Log for deleted messages
            filter_del = ChannelAdminLogEventsFilter(delete=True)
            res = await client(GetAdminLogRequest(
                channel=entity,
                q='',
                events_filter=filter_del,
                max_id=0,
                min_id=0,
                limit=50
            ))
            print(f"Found {len(res.events)} admin log events!")
            for event in res.events:
                action = event.action
                msg = getattr(action, 'message', None)
                if msg:
                    print(f"  [Event {event.id}] Msg ID: {msg.id}, Date: {msg.date}, Media: {type(msg.media).__name__ if msg.media else 'None'}")
                    print(f"  Text: {msg.message}")
        except Exception as e:
            print(f"Error checking {gid}: {e}")
            
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_admin_log())
