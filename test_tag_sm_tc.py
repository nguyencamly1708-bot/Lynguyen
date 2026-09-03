import os
import sys
import httpx
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def get_sm_tc_tags_for_group(client: httpx.AsyncClient, chat_id: str) -> str:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatAdministrators"
    matched_tags = []
    
    try:
        res = await client.post(url, data={"chat_id": chat_id})
        if res.status_code == 200:
            data = res.json()
            if data.get("ok"):
                admins = data.get("result", [])
                for a in admins:
                    user = a.get("user", {})
                    user_id = user.get("id")
                    first_name = user.get("first_name", "")
                    last_name = user.get("last_name", "")
                    username = user.get("username", "")
                    c_title = a.get("custom_title", "")
                    
                    full_name = f"{first_name} {last_name}".strip()
                    search_str = f"{full_name} {username} {c_title}".lower()

                    # Check xem có chứa từ "sm" hoặc "tc" dạng độc lập hoặc trong tên/mã
                    if "sm" in search_str or "tc" in search_str:
                        if username:
                            matched_tags.append(f"@{username}")
                        elif user_id:
                            matched_tags.append(f"[{full_name}](tg://user?id={user_id})")
    except Exception as e:
        print("Lỗi getChatAdministrators:", e)

    if matched_tags:
        return " ".join(matched_tags)
    return "@sm @tc"

# Run simple sync wrapper for testing
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        tags = await get_sm_tc_tags_for_group(client, "-5300068522")
        print("Resulting tags:", tags)

asyncio.run(main())
