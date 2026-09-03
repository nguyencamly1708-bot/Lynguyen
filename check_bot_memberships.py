import asyncio
import json
import os
import sys
from dotenv import load_dotenv
import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUPS_FILE = "groups.json"

async def check_active_groups():
    if not os.path.exists(GROUPS_FILE):
        print("Không tìm thấy file groups.json")
        return

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        groups = json.load(f)

    print(f"🔍 Đang kiểm tra thực tế Bot @teamSCM_bot trong {len(groups)} nhóm...")

    active_groups = {}
    not_member_groups = []

    bot_id = 8880358091

    async with httpx.AsyncClient(timeout=10.0) as client:
        for gid, gdata in list(groups.items()):
            gtitle = gdata.get("title", f"Nhóm {gid}")
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
            try:
                res = await client.post(url, data={"chat_id": gid, "user_id": bot_id})
                if res.status_code == 200 and res.json().get("ok"):
                    member_status = res.json().get("result", {}).get("status")
                    if member_status in ["member", "administrator", "creator", "restricted"]:
                        active_groups[gid] = gdata
                        print(f"✅ BOT ĐÃ THAM GIA: {gtitle} ({gid}) - Trạng thái: {member_status}")
                    else:
                        not_member_groups.append((gid, gtitle))
                else:
                    not_member_groups.append((gid, gtitle))
            except Exception as e:
                not_member_groups.append((gid, gtitle))
            
            await asyncio.sleep(0.1)

    print(f"\n📊 KẾT QUẢ KIỂM TRA THỰC TẾ:")
    print(f" • Số nhóm Bot @teamSCM_bot ĐÃ THAM GIA: {len(active_groups)} nhóm")
    print(f" • Số nhóm Bot CHƯA THAM GIA: {len(not_member_groups)} nhóm")

if __name__ == "__main__":
    asyncio.run(check_active_groups())
