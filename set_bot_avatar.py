import os
import sys
import httpx
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
IMAGE_PATH = r"C:\Users\Admin\.gemini\antigravity\brain\0d8cad12-c5f3-47cd-af06-6510b1cc4911\.user_uploaded\media__1785685230015.png"

if not os.path.exists(IMAGE_PATH):
    print("❌ Không tìm thấy file ảnh!")
    sys.exit(1)

print(f"Đang cài đặt avatar cho Bot Telegram từ file: {IMAGE_PATH}...")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyProfilePhoto"

with open(IMAGE_PATH, "rb") as f:
    photo_bytes = f.read()

# Telegram API setMyProfilePhoto mong đợi param photo dạng JSON object InputProfilePhotoStatic hoặc file upload
files = {"photo": ("avatar.png", photo_bytes, "image/png")}

with httpx.Client(timeout=30.0) as client:
    res = client.post(url, files=files)
    print("HTTP Response Code:", res.status_code)
    print("Response Body:", res.text)
