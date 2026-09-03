import os
import sys
import json
import asyncio
from dotenv import load_dotenv

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "31301997"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "5238dcc8bb48b6e7c0eccf28bf15d468")
PHONE = "+84927463872"
SESSION_NAME = "jinli072_userbot"
AUTH_CACHE_FILE = "auth_cache.json"

async def main():
    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), SESSION_NAME)
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"ALREADY_AUTHORIZED: Tài khoản đã đăng nhập trước đó: @{me.username} ({me.phone})")
        await client.disconnect()
        return

    print(f"Đang gửi yêu cầu mã xác nhận OTP tới số điện thoại: {PHONE} ...")
    try:
        sent_code = await client.send_code_request(PHONE)
        cache_data = {
            "phone": PHONE,
            "phone_code_hash": sent_code.phone_code_hash
        }
        cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), AUTH_CACHE_FILE)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)
        print("CODE_SENT_SUCCESS: Đã gửi mã xác nhận thành công về ứng dụng Telegram!")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
