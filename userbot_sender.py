import os
import sys
import asyncio
import re
import html
import logging
from dotenv import load_dotenv

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telethon import TelegramClient

logger = logging.getLogger(__name__)

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "31301997"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "5238dcc8bb48b6e7c0eccf28bf15d468")
SESSION_NAME = "jinli072_userbot"

_client = None
_client_lock = asyncio.Lock()

def get_session_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), SESSION_NAME)

async def get_connected_client() -> TelegramClient:
    global _client
    async with _client_lock:
        if _client is None:
            _client = TelegramClient(get_session_path(), API_ID, API_HASH)
            await _client.connect()
        elif not _client.is_connected():
            await _client.connect()
        return _client

async def is_authorized() -> bool:
    """Kiểm tra xem tài khoản @JinLi072 đã đăng nhập session chưa."""
    try:
        client = await get_connected_client()
        return await client.is_user_authorized()
    except Exception as e:
        logger.warning(f"Lỗi kiểm tra userbot auth: {e}")
        return False

async def get_user_dialogs():
    """Lấy danh sách tất cả các nhóm chat mà tài khoản @JinLi072 đã tham gia."""
    client = await get_connected_client()
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

async def get_group_sm_tc_tags(chat_id: int) -> str:
    """
    Quét danh sách thành viên trong nhóm Telegram có tên chứa SM hoặc TC.
    Tạo link tag HTML dạng <a href='tg://user?id=...'>Tên Hiển Thị</a>
    giống chính xác định dạng tin nhắn của Đối Soát SCM.
    """
    try:
        client = await get_connected_client()
        entity = await client.get_entity(chat_id)
        participants = await client.get_participants(entity, limit=200)
        
        tags = []
        seen_ids = set()
        
        for p in participants:
            full_name = f"{p.first_name or ''} {p.last_name or ''}".strip()
            username = p.username or ""
            combined = f"{full_name} @{username}".lower()

            # Kiểm tra xem có chứa từ SM hoặc TC không
            if any(k in combined for k in [" sm ", " tc ", "-sm-", "-tc-", "_sm_", "_tc_"]) or \
               re.search(r"\b(SM|TC)\b", f"{full_name} {username}", re.IGNORECASE):
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    escaped_name = html.escape(full_name) if full_name else (f"@{username}" if username else "Thành viên")
                    tags.append(f'<a href="tg://user?id={p.id}">{escaped_name}</a>')

        return "\n".join(tags)
    except Exception as e:
        logger.warning(f"Lỗi lấy tag SM/TC cho chat {chat_id}: {e}")
        return ""

async def send_message_as_user(chat_id: int, message: str, file_path: str = None, parse_mode: str = "html"):
    """
    Gửi tin nhắn hoặc file ảnh đính kèm dưới danh nghĩa tài khoản cá nhân @JinLi072.
    """
    client = await get_connected_client()
    if file_path and os.path.exists(file_path):
        sent = await client.send_file(chat_id, file_path, caption=message, parse_mode=parse_mode)
    else:
        sent = await client.send_message(chat_id, message, parse_mode=parse_mode)

    return {
        "success": True,
        "message_id": sent.id,
        "chat_id": chat_id
    }

if __name__ == "__main__":
    async def main():
        auth = await is_authorized()
        print(f"Trạng thái đăng nhập của @JinLi072: {'ĐÃ ĐĂNG NHẬP' if auth else 'CHƯA ĐĂNG NHẬP'}")
        if auth:
            tag_demo = await get_group_sm_tc_tags(-4903740099)
            print(f"Demo SM/TC tags cho AV4 (-4903740099):\n{tag_demo}")

    asyncio.run(main())
