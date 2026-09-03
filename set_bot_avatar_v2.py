import os
import sys
import json
import httpx
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
IMAGE_PATH = r"C:\Users\Admin\.gemini\antigravity\brain\0d8cad12-c5f3-47cd-af06-6510b1cc4911\.user_uploaded\media__1785685230015.png"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyProfilePhoto"

with open(IMAGE_PATH, "rb") as f:
    photo_bytes = f.read()

# Theo Telegram Bot API doc cho setMyProfilePhoto:
# Param "photo" là InputProfilePhoto: {"type": "static", "photo": "attach://photo_file"}
photo_struct = json.dumps({"type": "static", "photo": "attach://photo_file"})

data = {"photo": photo_struct}
files = {"photo_file": ("avatar.png", photo_bytes, "image/png")}

with httpx.Client(timeout=30.0) as client:
    res = client.post(url, data=data, files=files)
    print("HTTP Response Code:", res.status_code)
    print("Response Body:", res.text)
