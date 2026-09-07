import asyncio
import sys
import os
import json
import re
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from telethon import TelegramClient

scratch_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"
session_path = os.path.join(scratch_dir, "jinli072_userbot")

API_ID = 39866164
API_HASH = "c0612f0ffb574a44f51f496191ef6453"

# List of 37 store IDs from sheet
STORE_IDS = [
    "A101", "A104", "A105", "A107", "A131", "A135", "A136", "A139", "A140", "A141",
    "A144", "A148", "A150", "A151", "A161", "A163", "A170", "A175", "A183", "A186",
    "A187", "A192", "A201", "A208", "A218", "A223", "A225", "AKR", "BTH", "BVB",
    "CKO", "CLG", "CTH", "D10", "DXH", "ECG", "EHS"
]

def find_dc_group_for_st(st_id: str, groups: list):
    st_upper = st_id.strip().upper()
    dc_groups = [g for g in groups if g.get("category") == "dc" or "dc" in g.get("name", "").lower()]
    for g in dc_groups:
        title = g.get("name", "")
        # Exact word match
        if re.search(rf"\b{re.escape(st_upper)}\b", title, re.IGNORECASE):
            return g
    return None

async def delete_direct():
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("Not authorized", flush=True)
        return

    me = await client.get_me()
    print(f"Connected as {me.id} ({me.first_name})", flush=True)

    with open(r"h:\My Drive\Lynguyen\groups.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        groups = [{"id": k, "name": v.get("title", ""), "category": v.get("category", "")} for k, v in data.items()]
    else:
        groups = data

    cutoff = datetime.now(timezone.utc) - timedelta(hours=3)
    deleted_total = 0

    # 1. Check A131 first
    target_groups = []
    a131_g = {"id": -5167161385, "name": "DC Dry - A131 (B01.05 Dream Home Palace)"}
    target_groups.append(a131_g)

    # 2. Check all other 36 stores
    for st in STORE_IDS:
        matched = find_dc_group_for_st(st, groups)
        if matched and matched["id"] != a131_g["id"]:
            target_groups.append(matched)

    print(f"Checking {len(target_groups)} specific DC groups for sent messages...", flush=True)

    for g in target_groups:
        gid = int(g["id"])
        gname = g["name"]
        try:
            entity = await client.get_entity(gid)
            to_del = []
            async for msg in client.iter_messages(entity, limit=15):
                # If message is recent and sent by userbot
                if msg.date >= cutoff:
                    txt = (msg.text or "")
                    # Match any message sent by me or containing the broadcast text/table
                    if msg.out or msg.sender_id == me.id or "phiếu đổi trả" in txt.lower() or "đối soát" in txt.lower():
                        to_del.append(msg.id)
                        print(f"  Found in '{gname}' msg ID {msg.id} at {msg.date}: {txt[:35].replace(chr(10), ' ')}", flush=True)
            if to_del:
                await client.delete_messages(entity, to_del, revoke=True)
                print(f"  ===> [REVOKED FOR EVERYONE] Deleted {len(to_del)} messages in '{gname}'!", flush=True)
                deleted_total += len(to_del)
        except Exception as e:
            print(f"  Could not access '{gname}' ({gid}): {e}", flush=True)

    print(f"\n==========================================", flush=True)
    print(f"TOTAL MESSAGES DELETED IN GROUPS: {deleted_total}!", flush=True)
    print(f"==========================================", flush=True)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(delete_direct())
