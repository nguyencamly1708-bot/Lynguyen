import asyncio
import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

from userbot_sender import get_client

# Test 5 sample groups
sample_chats = [
    (-4903740099, "AV4 - DC"),
    (-4887768556, "A101 - DC"),
    (-4728069825, "A104 - DC"),
    (-4867362624, "A105 - DC"),
    (-5224980650, "A148 - DC")
]

async def check():
    client = get_client()
    async with client:
        for cid, name in sample_chats:
            try:
                entity = await client.get_entity(cid)
                participants = await client.get_participants(entity, limit=200)
                sm_tc = []
                for p in participants:
                    full_name = f"{p.first_name or ''} {p.last_name or ''}".strip()
                    username = p.username or ""
                    combined = f"{full_name} @{username}".lower()
                    if any(k in combined for k in [" sm ", " tc ", "-sm-", "-tc-", "_sm_", "_tc_"]) or \
                       re.search(r"\b(SM|TC)\b", f"{full_name} {username}", re.IGNORECASE):
                        sm_tc.append((p.id, full_name))
                print(f"Group {name} ({cid}): Found {len(sm_tc)} SM/TC:")
                for u in sm_tc:
                    print(f"   -> ID={u[0]}: {u[1]}")
            except Exception as e:
                print(f"Group {name} ({cid}) Error: {e}")

asyncio.run(check())
