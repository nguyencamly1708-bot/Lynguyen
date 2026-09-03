import os
import sys
import httpx
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Test data mẫu theo đúng hình screenshot 2 của người dùng
sample_admins = [
    {"user_id": 1001, "full_name": "HCM24 - Q7R - TC - Thuận Trần - SC004980"},
    {"user_id": 1002, "full_name": "HCM24 - Q7R - SM - Trang Huỳnh - SC005602"},
    {"user_id": 1003, "full_name": "HCM24 - RVS - GSM - Duy Phạm - SC005141"}
]

tags_list = []
for member in sample_admins:
    full_name = member["full_name"]
    uid = member["user_id"]
    tags_list.append(f"[{full_name}](tg://user?id={uid})")

final_tags_text = "\n".join(tags_list)

caption_text = (
    "Ly gửi DS phiếu đối trả của tuần W29.2026 DC chưa nhận được hàng/chưa nhận được chứng từ.\n"
    "Hàng thực tế nếu đã bàn giao cho VT anh chị gửi giúp Ly ảnh chụp Phiếu chuyển/PGH.\n\n"
    "*Sau hôm nay SCM sẽ trả tồn những phiếu này về ST.\n"
    "Cảm ơn các anh chị.\n\n"
    f"{final_tags_text}"
)

print("--- NỘI DUNG TIN NHẮN THEO ĐÚNG ĐỊNH DẠNG ĐỐI SOÁT SCM ---")
print(caption_text)
