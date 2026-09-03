import asyncio
import sys
import io

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from userbot_sender import get_user_dialogs, is_authorized

async def main():
    auth = await is_authorized()
    print("Xác thực @JinLi072:", "THÀNH CÔNG" if auth else "THẤT BẠI")
    if auth:
        dialogs = await get_user_dialogs()
        print(f"Tổng số nhóm/kênh @JinLi072 đã tham gia: {len(dialogs)}")
        for idx, d in enumerate(dialogs[:10], 1):
            print(f"{idx}. [{d['id']}] {d['title']}")

if __name__ == "__main__":
    asyncio.run(main())
