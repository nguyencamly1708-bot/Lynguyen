import asyncio
import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

from userbot_sender import get_client

async def test_get_participants():
    client = get_client()
    async with client:
        # Check AV4 group or any DC group
        # Let's find AV4: -4903740099
        chat_id = -4903740099
        print(f"Connecting to chat {chat_id}...")
        try:
            entity = await client.get_entity(chat_id)
            print(f"Group: {entity.title}")
            participants = await client.get_participants(entity, limit=200)
            print(f"Total participants fetched: {len(participants)}")
            sm_tc_users = []
            for p in participants:
                full_name = f"{p.first_name or ''} {p.last_name or ''}".strip()
                username = f"@{p.username}" if p.username else ""
                combined = f"{full_name} {username}"
                # check SM or TC
                if re.search(r"\b(SM|TC)\b", combined, re.IGNORECASE) or " SM " in combined or " TC " in combined or "-SM-" in combined or "-TC-" in combined or combined.startswith("SM ") or combined.startswith("TC "):
                    sm_tc_users.append((p.id, full_name, username))
                    print(f"  Found SM/TC: ID={p.id}, Name='{full_name}', Username='{username}'")

            print(f"Total SM/TC found: {len(sm_tc_users)}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_get_participants())
