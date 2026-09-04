import os
import sys
import json
import asyncio

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from userbot_sender import get_user_dialogs, is_authorized

GROUPS_FILE = "groups.json"

async def sync_groups():
    auth = await is_authorized()
    if not auth:
        print("ERROR: Chưa đăng nhập tài khoản @JinLi072!")
        return 0

    print("Đang quét danh sách nhóm từ tài khoản @JinLi072...")
    dialogs = await get_user_dialogs()

    groups_data = {}
    for d in dialogs:
        gid = str(d["id"])
        title = d["title"].strip()
        gtype = d["entity_type"]

        # Tự động phân loại category
        title_lower = title.lower()
        if "krc" in title_lower or "rau" in title_lower:
            category = "krc"
        elif "aba" in title_lower:
            category = "aba"
        elif "dc" in title_lower:
            category = "dc"
        else:
            category = "other"

        groups_data[gid] = {
            "title": title,
            "type": gtype,
            "category": category,
            "unread_count": d.get("unread_count", 0)
        }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    groups_path = os.path.join(script_dir, GROUPS_FILE)

    with open(groups_path, "w", encoding="utf-8") as f:
        json.dump(groups_data, f, ensure_ascii=False, indent=2)

    print(f"ĐỒNG BỘ THÀNH CÔNG: Đã lưu {len(groups_data)} nhóm vào {GROUPS_FILE}!")
    return len(groups_data)

if __name__ == "__main__":
    asyncio.run(sync_groups())
