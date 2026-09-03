import os
import sys
import httpx
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "-5300068522"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatAdministrators"

with httpx.Client(timeout=15.0) as client:
    res = client.post(url, data={"chat_id": CHAT_ID})
    print("Status:", res.status_code)
    data = res.json()
    if data.get("ok"):
        admins = data.get("result", [])
        print(f"Tìm thấy {len(admins)} admin trong nhóm:")
        for a in admins:
            user = a.get("user", {})
            c_title = a.get("custom_title", "")
            first_name = user.get("first_name", "")
            last_name = user.get("last_name", "")
            username = user.get("username", "")
            user_id = user.get("id")
            full_name = f"{first_name} {last_name}".strip()
            print(f" -> User ID: {user_id} | Name: '{full_name}' | Username: @{username} | Custom Title: '{c_title}'")
    else:
        print("Lỗi:", data)
