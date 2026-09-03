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
from telethon.errors import SessionPasswordNeededError

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "31301997"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "5238dcc8bb48b6e7c0eccf28bf15d468")
SESSION_NAME = "jinli072_userbot"
AUTH_CACHE_FILE = "auth_cache.json"

async def main():
    if len(sys.argv) < 2:
        print("USAGE: python finish_login.py <CODE> [PASSWORD]")
        return

    code = sys.argv[1].strip()
    password = sys.argv[2].strip() if len(sys.argv) > 2 else "cfdpvudQ6aw"

    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), AUTH_CACHE_FILE)
    if not os.path.exists(cache_path):
        print("ERROR: Không tìm thấy auth_cache.json, vui lòng gửi lại mã yêu cầu OTP!")
        return

    with open(cache_path, "r", encoding="utf-8") as f:
        cache = json.load(f)

    phone = cache["phone"]
    phone_code_hash = cache["phone_code_hash"]

    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), SESSION_NAME)
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    try:
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except SessionPasswordNeededError:
            print("Tài khoản yêu cầu mật khẩu 2 lớp (2FA). Đang thử xác thực với mật khẩu...")
            await client.sign_in(password=password)

        me = await client.get_me()
        print("\n" + "=" * 60)
        print("ĐĂNG NHẬP THÀNH CÔNG VỚI TƯ CÁCH USER CÁ NHÂN!")
        print(f"Họ tên: {me.first_name} {me.last_name or ''}")
        print(f"Username: @{me.username}")
        print(f"User ID: {me.id}")
        print(f"Phone: {me.phone}")
        print("=" * 60)
    except Exception as e:
        print(f"LOGIN_ERROR: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
