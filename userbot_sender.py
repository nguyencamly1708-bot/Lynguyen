import os
import sys
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
SESSION_NAME = "jinli072_userbot"

def get_client():
    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), SESSION_NAME)
    return TelegramClient(session_path, API_ID, API_HASH)

async def is_authorized() -> bool:
    """Kiểm tra xem tài khoản @JinLi072 đã đăng nhập session chưa."""
    client = get_client()
    async with client:
        return await client.is_user_authorized()

async def get_user_dialogs():
    """Lấy danh sách tất cả các nhóm chat mà tài khoản @JinLi072 đã tham gia."""
    client = get_client()
    async with client:
        dialogs = []
        async for d in client.iter_dialogs():
            if d.is_group or d.is_channel:
                dialogs.append({
                    "id": d.id,
                    "title": d.title,
                    "entity_type": "channel" if d.is_channel else "group",
                    "unread_count": d.unread_count
                })
        return dialogs

async def send_message_as_user(chat_id: int, message: str, file_path: str = None):
    """Gửi tin nhắn hoặc file đính kèm dưới danh nghĩa tài khoản cá nhân @JinLi072."""
    client = get_client()
    async with client:
        if file_path and os.path.exists(file_path):
            sent = await client.send_file(chat_id, file_path, caption=message)
        else:
            sent = await client.send_message(chat_id, message)
        return {
            "success": True,
            "message_id": sent.id,
            "chat_id": chat_id
        }

if __name__ == "__main__":
    async def check():
        auth = await is_authorized()
        print(f"Trạng thái đăng nhập của tài khoản @JinLi072: {'ĐÃ ĐĂNG NHẬP' if auth else 'CHƯA ĐĂNG NHẬP'}")
    asyncio.run(check())
