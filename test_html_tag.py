import os
import sys
import httpx
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "-5300068522"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

caption_text = (
    "Ly gửi DS phiếu đối trả của tuần W29.2026 DC chưa nhận được hàng/chưa nhận được chứng từ.\n"
    "Hàng thực tế nếu đã bàn giao cho VT anh chị gửi giúp Ly ảnh chụp Phiếu chuyển/PGH.\n\n"
    "<b>*Sau hôm nay SCM sẽ trả tồn những phiếu này về ST.</b>\n"
    "Cảm ơn các anh chị.\n\n"
    '<a href="tg://user?id=8493929214">KFM - SCM - Ly Nguyễn - SC015148</a>'
)

with httpx.Client(timeout=15.0) as client:
    res = client.post(url, json={"chat_id": CHAT_ID, "text": caption_text, "parse_mode": "HTML"})
    print("Status Code:", res.status_code)
    print("Response:", res.text)
