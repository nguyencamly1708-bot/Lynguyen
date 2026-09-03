import os
import sys
from dotenv import load_dotenv

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telethon import TelegramClient

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID", "31301997")
API_HASH = os.getenv("TELEGRAM_API_HASH", "5238dcc8bb48b6e7c0eccf28bf15d468")
SESSION_NAME = "jinli072_userbot"

def main():
    print("=" * 60)
    print("ĐĂNG NHẬP TELEGRAM USERBOT CHO TÀI KHOẢN @JinLi072")
    print(f"API_ID: {API_ID}")
    print("=" * 60)

    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

    async def init():
        await client.start()
        me = await client.get_me()
        print("\n" + "=" * 60)
        print("ĐĂNG NHẬP THÀNH CÔNG!")
        print(f"Tên: {me.first_name} {me.last_name or ''}")
        print(f"Username: @{me.username}")
        print(f"User ID: {me.id}")
        print(f"Số điện thoại: {me.phone}")
        print("File session đã được lưu tại:", os.path.abspath(f"{SESSION_NAME}.session"))
        print("=" * 60)

    with client:
        client.loop.run_until_complete(init())

if __name__ == "__main__":
    main()
