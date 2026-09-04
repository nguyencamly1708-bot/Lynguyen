import asyncio
import csv
import datetime
import html
import io
import json
import logging
import os
import shutil
import sys
from contextlib import asynccontextmanager
from typing import List, Optional

from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openpyxl
from PIL import Image, ImageDraw, ImageFont

# Cấu hình mã hóa UTF-8 cho Windows stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_BASE_URL = os.getenv("PUBLIC_DASHBOARD_URL", "https://barrel-kodak-jane-residents.trycloudflare.com")
GROUPS_FILE = "groups.json"
HISTORY_FILE = "history.json"
MENTIONS_FILE = "mentions.json"
MEMBERS_FILE = "members.json"
UPLOAD_DIR = "uploads"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"

os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Helpers dữ liệu
def load_json(filepath: str, default=None):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default if default is not None else {}
    return default if default is not None else {}

def save_json(filepath: str, data) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def track_member(chat_id: int, user) -> None:
    if not user or user.is_bot:
        return
    chat_id_str = str(chat_id)
    user_id_str = str(user.id)
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else ""

    members_data = load_json(MEMBERS_FILE, {})
    if chat_id_str not in members_data:
        members_data[chat_id_str] = {}

    if user_id_str not in members_data[chat_id_str] or members_data[chat_id_str][user_id_str].get("full_name") != full_name:
        members_data[chat_id_str][user_id_str] = {
            "user_id": user.id,
            "full_name": full_name,
            "username": username
        }
        save_json(MEMBERS_FILE, members_data)
        logger.info(f"👤 Đã ghi nhận thành viên nhóm ({chat_id}): {full_name}")

class BroadcastRequest(BaseModel):
    message: str
    target_groups: list[str]

class SyncSheetRequest(BaseModel):
    target_groups: list[str]

import re

def find_dc_group_for_st(groups: dict, id_st: str):
    """
    Tìm nhóm DC phù hợp cho ID ST trong groups.json:
    Ưu tiên 1: Nhóm có chữ DC và chứa ID ST dưới dạng từ riêng biệt.
    Ưu tiên 2: Nhóm chứa 'DC - ID ST' hoặc 'ID ST - DC'.
    Ưu tiên 3: Bất kỳ nhóm nào chứa ID ST.
    """
    id_st_clean = id_st.strip()
    pattern = re.compile(rf"\b{re.escape(id_st_clean)}\b", re.IGNORECASE)

    # 1. Nhóm có chữ DC và chứa ID ST
    for gid, gdata in groups.items():
        title = gdata.get("title", "")
        cat = gdata.get("category", "")
        is_dc = (cat == "dc") or ("DC" in title.upper())
        if is_dc and pattern.search(title):
            return int(gid), title

    # 2. Nhóm chứa 'DC - ID ST' hoặc 'ID ST - DC'
    for gid, gdata in groups.items():
        title = gdata.get("title", "")
        if f"dc - {id_st_clean}".lower() in title.lower() or f"{id_st_clean} - dc".lower() in title.lower():
            return int(gid), title

    # 3. Bất kỳ nhóm nào chứa ID ST
    for gid, gdata in groups.items():
        title = gdata.get("title", "")
        if pattern.search(title):
            return int(gid), title

    return None, None

# Hàm tạo Bảng Ảnh PNG chuẩn mẫu "Đối soát SCM" (Header xanh lá, Bảng viền cam chuẩn ảnh mẫu)
def generate_st_table_image(id_st: str, items: list, output_path: str):
    headers = ["ID ST", "Mã phiếu", "Mã hàng", "Tên Hàng", "ĐVT", "SL chuyển"]

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 22)
        font_header = ImageFont.truetype("arialbd.ttf", 13)
        font_row = ImageFont.truetype("arial.ttf", 13)
        font_row_bold = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = font_title
        font_row = font_title
        font_row_bold = font_title

    min_widths = [75, 110, 120, 280, 65, 95]
    col_widths = list(min_widths)

    for item in items:
        row_vals = [
            item.get("id_st", id_st),
            item.get("ma_phieu", ""),
            item.get("ma_hang", ""),
            item.get("ten_hang", ""),
            item.get("dvt", ""),
            str(item.get("sl_chuyen", ""))
        ]
        for i, val in enumerate(row_vals):
            bbox = font_row.getbbox(str(val))
            w = (bbox[2] - bbox[0]) + 24
            if w > col_widths[i]:
                col_widths[i] = w

    table_width = sum(col_widths)
    margin_x = 16
    margin_y = 16
    title_height = 48
    header_height = 36
    row_height = 34

    total_width = table_width + (margin_x * 2)
    total_height = margin_y + title_height + header_height + (len(items) * row_height) + margin_y

    img = Image.new("RGB", (total_width, total_height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # 1. Tiêu đề "Đối soát SCM" chữ xanh lá
    draw.text((margin_x + 4, margin_y + 8), "Đối soát SCM", fill=(34, 197, 94), font=font_title)

    # 2. Header bảng màu Cam #EA580C
    header_y = margin_y + title_height
    draw.rectangle(
        [margin_x, header_y, margin_x + table_width, header_y + header_height],
        fill=(234, 88, 12)
    )

    curr_x = margin_x
    for i, h in enumerate(headers):
        draw.text((curr_x + 10, header_y + 9), h, fill=(255, 255, 255), font=font_header)
        curr_x += col_widths[i]

    # 3. Dòng dữ liệu xen kẽ
    curr_y = header_y + header_height
    for idx, item in enumerate(items):
        bg = (255, 255, 255) if idx % 2 == 0 else (248, 250, 252)
        draw.rectangle(
            [margin_x, curr_y, margin_x + table_width, curr_y + row_height],
            fill=bg,
            outline=(226, 232, 240)
        )

        row_vals = [
            item.get("id_st", id_st),
            item.get("ma_phieu", ""),
            item.get("ma_hang", ""),
            item.get("ten_hang", ""),
            item.get("dvt", ""),
            str(item.get("sl_chuyen", ""))
        ]

        curr_x = margin_x
        for i, val in enumerate(row_vals):
            val_str = str(val)
            f = font_row_bold if i in [0, 1] else font_row
            color = (15, 23, 42)
            draw.text((curr_x + 10, curr_y + 8), val_str, fill=color, font=f)
            curr_x += col_widths[i]

        curr_y += row_height

    # Viền bao ngoài bảng
    draw.rectangle(
        [margin_x, header_y, margin_x + table_width, curr_y],
        outline=(203, 213, 225),
        width=1
    )

    img.save(output_path)
    return output_path

# Quản lý Lifespan chạy Bot Polling song song
@asynccontextmanager
async def lifespan(app: FastAPI):
    if BOT_TOKEN and BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        try:
            from telegram import Update
            from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, ChatJoinRequestHandler, filters

            async def auto_approve_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                req = update.chat_join_request
                if not req:
                    return
                chat = req.chat
                user = req.from_user
                try:
                    await context.bot.approve_chat_join_request(
                        chat_id=chat.id,
                        user_id=user.id
                    )
                    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                    logger.info(f"✅ [AUTO ACCEPT] Đã tự động chấp nhận {full_name} (@{user.username or user.id}) tham gia nhóm '{chat.title}' ({chat.id})")
                    track_member(chat.id, user)
                except Exception as e:
                    logger.error(f"❌ [AUTO ACCEPT FAILED] Lỗi duyệt user {user.id} vào nhóm {chat.id}: {e}")

            async def track_group(update: Update) -> None:
                chat = update.effective_chat
                if chat and chat.type in ["group", "supergroup"]:
                    groups = load_json(GROUPS_FILE, {})
                    chat_id_str = str(chat.id)
                    if chat_id_str not in groups or groups[chat_id_str].get("title") != chat.title:
                        groups[chat_id_str] = {"title": chat.title, "type": chat.type}
                        save_json(GROUPS_FILE, groups)
                        logger.info(f"Đã lưu nhóm Telegram mới: {chat.title} ({chat.id})")

                    if update.effective_user:
                        track_member(chat.id, update.effective_user)

                    msg = update.effective_message
                    if msg and msg.new_chat_members:
                        for u in msg.new_chat_members:
                            track_member(chat.id, u)

            async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await track_group(update)
                user_name = update.effective_user.first_name
                await update.message.reply_text(
                    f"👋 **Chào {user_name}!**\nBot `teamSCM_bot` đã kết nối thành công và sẵn sàng tự động phát tin theo ID ST!",
                    parse_mode="Markdown"
                )

            async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await track_group(update)

                msg = update.effective_message
                if not msg:
                    return

                text = msg.text or msg.caption or ""
                text_lower = text.lower()
                sender = msg.from_user
                chat = msg.chat

                # 1. Kiểm tra Tag @teamSCM_bot, @DoisoatSCM_bot hoặc @JinLi072
                has_tag = any(bot_tag in text_lower for bot_tag in ["teamscm_bot", "doisoatscm_bot", "jinli072"])

                # 2. Kiểm tra Entity Mentions của Telegram
                entities = msg.entities or msg.caption_entities or []
                for entity in entities:
                    if entity.type in ["mention", "text_mention"]:
                        mention_text = text[entity.offset : entity.offset + entity.length].lower()
                        if any(bot_tag in mention_text for bot_tag in ["teamscm_bot", "doisoatscm_bot", "jinli072"]):
                            has_tag = True

                # 3. Kiểm tra xem có phải tin nhắn Reply lại Bot hoặc Reply lại @JinLi072
                is_reply = False
                if msg.reply_to_message and msg.reply_to_message.from_user:
                    reply_user = msg.reply_to_message.from_user
                    if reply_user.is_bot or (reply_user.username and reply_user.username.lower() in ["teamscm_bot", "doisoatscm_bot", "jinli072"]):
                        is_reply = True


                if has_tag or is_reply:
                    mentions = load_json(MENTIONS_FILE, [])
                    sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() if sender else "Người dùng"
                    sender_username = f"@{sender.username}" if sender and sender.username else ""

                    mention_entry = {
                        "id": f"{chat.id}_{msg.message_id}",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "group_title": chat.title or "Chat riêng",
                        "group_id": str(chat.id),
                        "sender_name": sender_name,
                        "sender_username": sender_username,
                        "text": text,
                        "is_reply": is_reply,
                        "has_tag": has_tag,
                        "message_id": msg.message_id
                    }

                    if not any(m.get("id") == mention_entry["id"] for m in mentions):
                        mentions.append(mention_entry)
                        save_json(MENTIONS_FILE, mentions)
                        logger.info(f"📌 ĐÃ LƯU LƯỢT TAG/REPLY từ {sender_name} tại nhóm {chat.title}")

            telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
            telegram_app.add_handler(CommandHandler("start", start_cmd))
            telegram_app.add_handler(ChatJoinRequestHandler(auto_approve_join_request))
            telegram_app.add_handler(MessageHandler(filters.ALL, handle_msg))

            await telegram_app.initialize()
            await telegram_app.start()
            await telegram_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("🚀 Telegram Bot Polling (Auto Accept enabled) đã kích hoạt thành công!")
        except Exception as e:
            logger.error(f"Lỗi khởi động Telegram Bot: {e}")

    yield

app = FastAPI(title="Telegram Broadcast Dashboard", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/api/status")
async def get_status():
    groups = load_json(GROUPS_FILE, {})
    mentions = load_json(MENTIONS_FILE, [])
    userbot_auth = False
    try:
        from userbot_sender import is_authorized
        userbot_auth = await is_authorized()
    except Exception:
        userbot_auth = False

    return {
        "status": "online",
        "bot_token_valid": bool(BOT_TOKEN and BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE"),
        "userbot_auth": userbot_auth,
        "userbot_username": "JinLi072",
        "userbot_name": "Ly Nguyễn (@JinLi072)",
        "groups_count": len(groups),
        "mentions_count": len(mentions)
    }

@app.post("/api/userbot/sync_groups")
async def api_sync_userbot_groups():
    """Đồng bộ toàn bộ danh sách nhóm chat của @JinLi072 vào groups.json."""
    try:
        from sync_user_groups import sync_groups
        total = await sync_groups()
        return {"status": "success", "total_groups": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/groups")
async def get_groups():
    return load_json(GROUPS_FILE, {})

@app.get("/api/sldt/stores")
async def get_sldt_sheet_stores():
    """Lấy danh sách các ID ST đang có phiếu chờ xử lý trong Google Sheet cùng nhóm DC tương ứng."""
    try:
        grouped = fetch_and_parse_sheet()
        groups = load_json(GROUPS_FILE, {})
        matched_info = {}
        sheet_chat_ids = set()

        for st, items in grouped.items():
            gid, title = find_dc_group_for_st(groups, st)
            if gid:
                sheet_chat_ids.add(str(gid))
            matched_info[st] = {
                "items_count": len(items),
                "chat_id": str(gid) if gid else None,
                "group_title": title
            }

        return {
            "status": "success",
            "total_stores": len(grouped),
            "stores": matched_info,
            "sheet_group_ids": list(sheet_chat_ids)
        }
    except Exception as e:
        logger.warning(f"Lỗi get_sldt_sheet_stores: {e}")
        return {"status": "error", "detail": str(e), "stores": {}, "sheet_group_ids": []}

@app.get("/api/history")
async def get_history():
    return load_json(HISTORY_FILE, [])

@app.get("/api/mentions")
async def get_mentions():
    return load_json(MENTIONS_FILE, [])

@app.post("/api/clear_mentions")
async def clear_mentions():
    save_json(MENTIONS_FILE, [])
    return {"status": "cleared"}

# Hàm quét tự động danh sách Admin/Thành viên trong nhóm chứa chữ SM hoặc TC để tag đích danh (Chống lặp)
async def get_sm_tc_tags_for_group(client: httpx.AsyncClient, chat_id: int) -> str:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatAdministrators"
    matched_tags = []
    seen_user_ids = set()
    seen_usernames = set()
    seen_names = set()

    def add_user_tag(user_id=None, username="", full_name=""):
        nonlocal matched_tags, seen_user_ids, seen_usernames, seen_names

        clean_username = username.lstrip("@").strip() if username else ""
        norm_name = full_name.strip().lower()

        # Kiểm tra trùng lặp ID, username hoặc Tên
        if user_id and user_id in seen_user_ids:
            return
        if clean_username and clean_username.lower() in seen_usernames:
            return
        if norm_name and norm_name in seen_names:
            return

        # Ghi nhận đã xử lý
        if user_id:
            seen_user_ids.add(user_id)
        if clean_username:
            seen_usernames.add(clean_username.lower())
        if norm_name:
            seen_names.add(norm_name)

        # Ưu tiên tag @username nếu có, nếu không thì dùng thẻ HTML link theo user_id
        if clean_username:
            matched_tags.append(f"@{clean_username}")
        elif user_id and full_name:
            matched_tags.append(f'<a href="tg://user?id={user_id}">{html.escape(full_name)}</a>')
        elif user_id:
            matched_tags.append(f'<a href="tg://user?id={user_id}">Thành viên</a>')
        elif full_name:
            matched_tags.append(html.escape(full_name))

    # 1. Quét từ Telegram getChatAdministrators
    try:
        res = await client.post(url, data={"chat_id": str(chat_id)})
        if res.status_code == 200:
            data = res.json()
            if data.get("ok"):
                admins = data.get("result", [])
                for a in admins:
                    user = a.get("user", {})
                    if user.get("is_bot"):
                        continue

                    user_id = user.get("id")
                    first_name = user.get("first_name", "")
                    last_name = user.get("last_name", "")
                    username = user.get("username", "")
                    c_title = a.get("custom_title", "")
                    
                    full_name = f"{first_name} {last_name}".strip()
                    search_str = f"{full_name} {username} {c_title}".lower()

                    if any(k in search_str for k in ["sm", "tc"]):
                        add_user_tag(user_id=user_id, username=username, full_name=full_name)
    except Exception as e:
        logger.error(f"Lỗi getChatAdministrators: {e}")

    # 2. Quét từ file members.json
    try:
        members_data = load_json(MEMBERS_FILE, {})
        group_members = members_data.get(str(chat_id), {})
        for u_id_str, udata in group_members.items():
            user_id = udata.get("user_id")
            full_name = udata.get("full_name", "")
            username = udata.get("username", "")
            search_str = f"{full_name} {username}".lower()
            
            if any(k in search_str for k in ["sm", "tc"]):
                add_user_tag(user_id=user_id, username=username, full_name=full_name)
    except Exception as e:
        logger.error(f"Lỗi đọc members.json: {e}")

    # 3. Quét từ file mentions.json
    try:
        mentions = load_json(MENTIONS_FILE, [])
        for m in mentions:
            if m.get("group_id") == str(chat_id):
                s_name = m.get("sender_name", "")
                s_user = m.get("sender_username", "")
                s_str = f"{s_name} {s_user}".lower()
                if any(k in s_str for k in ["sm", "tc"]):
                    add_user_tag(username=s_user, full_name=s_name)
    except Exception:
        pass

    if matched_tags:
        return "\n".join(matched_tags)
    return ""

def fetch_and_parse_sheet():
    res = httpx.get(SHEET_CSV_URL, timeout=30.0, follow_redirects=True)
    if res.status_code != 200:
        raise Exception(f"Không thể kết nối Google Sheets! (Mã HTTP: {res.status_code})")

    content = res.content.decode("utf-8-sig", errors="ignore")
    rows = list(csv.reader(io.StringIO(content)))
    if not rows:
        raise Exception("Google Sheets rỗng!")

    # Cột AQ [Classify] = index 42
    # Cột AR [Xử lý] = index 43
    # Điều kiện để gửi tin spam ST:
    # 1. Cột AQ [Classify]: chỉ chọn "chờ ST phản hồi"
    # 2. Cột AR [Xử lý]: chỉ chọn "đang xử lý"
    grouped_by_st = {}
    for r in rows[1:]:
        if len(r) > 43:
            aq_val = r[42].strip().lower()
            ar_val = r[43].strip().lower()

            if "chờ st phản hồi" in aq_val and "đang xử lý" in ar_val:
                id_st = r[0].strip() if len(r) > 0 else "Khác"
                ngay_chuyen = r[1].strip() if len(r) > 1 else ""
                cn_chuyen = r[3].strip() if len(r) > 3 else ""
                cn_nhan = r[4].strip() if len(r) > 4 else ""
                ma_hang = r[8].strip() if len(r) > 8 else ""
                ten_hang = r[9].strip() if len(r) > 9 else ""
                dvt = r[10].strip() if len(r) > 10 else ""
                sl_chuyen = r[11].strip() if len(r) > 11 else ""
                ma_phieu = r[17].strip() if len(r) > 17 else ""
                trang_thai = r[20].strip() if len(r) > 20 else ""
                tg_tao = r[41].strip() if len(r) > 41 else ""

                if id_st not in grouped_by_st:
                    grouped_by_st[id_st] = []

                grouped_by_st[id_st].append({
                    "id_st": id_st,
                    "ngay_chuyen": ngay_chuyen,
                    "cn_chuyen": cn_chuyen,
                    "cn_nhan": cn_nhan,
                    "ma_hang": ma_hang,
                    "ten_hang": ten_hang,
                    "dvt": dvt,
                    "sl_chuyen": sl_chuyen,
                    "ma_phieu": ma_phieu,
                    "trang_thai": trang_thai,
                    "tg_tao": tg_tao
                })

    if not grouped_by_st:
        raise Exception("Không tìm thấy dòng dữ liệu nào thỏa điều kiện (Cột AQ='Chờ ST phản hồi' & Cột AR='Đang xử lý')!")

    return grouped_by_st

class SyncSheetRequest(BaseModel):
    custom_message: Optional[str] = None
    target_groups: Optional[List[str]] = None

# Endpoint ĐỒNG BỘ GOOGLE SHEET & PHÁT TIN ĐỐI SOÁT SLDT QUA USERBOT @JinLi072
@app.post("/api/sync_and_broadcast_st")
async def sync_and_broadcast_st(req: SyncSheetRequest):
    try:
        from userbot_sender import is_authorized as check_userbot_auth, send_message_as_user, get_group_sm_tc_tags
        userbot_active = await check_userbot_auth()
    except Exception as e:
        logger.warning(f"Lỗi import userbot_sender: {e}")
        userbot_active = False

    try:
        grouped_by_st = fetch_and_parse_sheet()
        groups = load_json(GROUPS_FILE, {})

        base_message = req.custom_message.strip() if (req.custom_message and req.custom_message.strip()) else "Ly gửi DS phiếu đối trả của tuần W29.2026 DC chưa nhận được hàng/chưa nhận được chứng từ.\nHàng thực tế nếu đã bàn giao cho VT anh chị gửi giúp Ly ảnh chụp Phiếu chuyển/PGH.\n\n*Sau hôm nay SCM sẽ trả tồn những phiếu này về ST.\nCảm ơn các anh chị."

        success_results = []
        failed_results = []
        sent_records = []

        async with httpx.AsyncClient(timeout=60.0) as http_client:
            for id_st, items in grouped_by_st.items():
                target_chat_ids = set()

                if req.target_groups:
                    # Gửi theo các nhóm người dùng tự chọn trên giao diện (chỉ gửi ST tương ứng với nhóm được tick)
                    pattern = re.compile(rf"\b{re.escape(id_st.strip())}\b", re.IGNORECASE)
                    for gid in req.target_groups:
                        cid = int(gid)
                        gtitle = groups.get(str(gid), {}).get("title", "")
                        if pattern.search(gtitle) or f"dc - {id_st.strip().lower()}" in gtitle.lower() or f"{id_st.strip().lower()} - dc" in gtitle.lower():
                            target_chat_ids.add(cid)
                    
                    if not target_chat_ids:
                        # Bỏ qua các ST khác không nằm trong các nhóm được tick chọn
                        continue
                else:
                    # Tự động tìm nhóm DC của ST theo tên ID ST ở cột A
                    dc_gid, dc_title = find_dc_group_for_st(groups, id_st)
                    if dc_gid:
                        target_chat_ids.add(dc_gid)

                if not target_chat_ids:
                    logger.warning(f"Không tìm thấy nhóm Telegram DC cho ID ST '{id_st}'")
                    failed_results.append(f"ST {id_st} (Chưa tìm thấy nhóm DC)")
                    continue

                # Tạo Bảng Ảnh SCM theo mẫu
                image_filename = f"table_{id_st}_{datetime.datetime.now().strftime('%H%M%S')}.png"
                image_path = os.path.join(UPLOAD_DIR, image_filename)
                generate_st_table_image(id_st, items, image_path)

                for chat_id in target_chat_ids:
                    gtitle = groups.get(str(chat_id), {}).get("title", f"Nhóm ({chat_id})")
                    try:
                        # 3. Tag tên những người trong nhóm có chữ SM và TC
                        sm_tc_tags = ""
                        if userbot_active:
                            try:
                                sm_tc_tags = await get_group_sm_tc_tags(chat_id)
                            except Exception as e:
                                logger.warning(f"Không lấy được SM/TC qua Telethon cho {chat_id}: {e}")

                        if not sm_tc_tags:
                            sm_tc_tags = await get_sm_tc_tags_for_group(http_client, chat_id)

                        tag_block = f"\n\n{sm_tc_tags}" if sm_tc_tags else ""
                        caption_text = f"{base_message}{tag_block}"

                        # Gửi tin nhắn qua tài khoản cá nhân @JinLi072 (hoặc Bot Token nếu userbot chưa đăng nhập)
                        if userbot_active:
                            send_res = await send_message_as_user(chat_id, caption_text, file_path=image_path, parse_mode="html")
                            msg_id = send_res.get("message_id")
                            if msg_id:
                                sent_records.append({
                                    "chat_id": chat_id,
                                    "group_title": gtitle,
                                    "message_id": msg_id,
                                    "revoked": False
                                })
                            success_results.append(f"ST {id_st} ➔ {gtitle} (@JinLi072)")
                        else:
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                            with open(image_path, "rb") as img_f:
                                files = {"photo": (image_filename, img_f.read(), "image/png")}
                                data = {"chat_id": str(chat_id), "caption": caption_text, "parse_mode": "HTML"}
                                res = await http_client.post(url, data=data, files=files)
                                if res.status_code == 200:
                                    res_data = res.json()
                                    msg_id = res_data.get("result", {}).get("message_id")
                                    if msg_id:
                                        sent_records.append({
                                            "chat_id": chat_id,
                                            "group_title": gtitle,
                                            "message_id": msg_id,
                                            "revoked": False
                                        })
                                    success_results.append(f"ST {id_st} ➔ {gtitle}")
                                else:
                                    failed_results.append(f"ST {id_st} ➔ {gtitle} ({res.text[:50]})")

                        await asyncio.sleep(1.5)
                    except Exception as e:
                        failed_results.append(f"ST {id_st} ➔ {gtitle} (Lỗi: {e})")

                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception:
                        pass

        sender_label = "@JinLi072" if userbot_active else "Bot"
        history = load_json(HISTORY_FILE, [])
        history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "sldt",
            "message": f"📊 Đối soát SLDT [{len(grouped_by_st)} ST] ({sender_label}) + Bảng Ảnh SCM",
            "total_target": len(grouped_by_st),
            "success_count": len(success_results),
            "failed_count": len(failed_results),
            "success_groups": success_results,
            "failed_groups": failed_results,
            "sent_records": sent_records,
            "revoked": False
        })
        save_json(HISTORY_FILE, history)

        return {
            "status": "completed",
            "sender": sender_label,
            "total_st": len(grouped_by_st),
            "success_results": success_results,
            "failed_results": failed_results
        }
    except Exception as e:
        logger.error(f"Lỗi sync_and_broadcast_st: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/broadcast")
async def broadcast_message(req: BroadcastRequest):
    return await send_broadcast_process(req.message, req.target_groups, [])

@app.post("/api/broadcast_media")
async def broadcast_media(
    message: str = Form(""),
    target_groups: str = Form("[]"),
    files: List[UploadFile] = File([])
):
    try:
        group_ids = json.loads(target_groups)
    except Exception:
        raise HTTPException(status_code=400, detail="Danh sách nhóm không hợp lệ!")

    saved_file_paths = []
    for file in files:
        if file.filename:
            file_path = os.path.join(UPLOAD_DIR, f"{datetime.datetime.now().timestamp()}_{file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_file_paths.append((file_path, file.filename, file.content_type or ""))

    result = await send_broadcast_process(message, group_ids, saved_file_paths)

    for fpath, _, _ in saved_file_paths:
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

    return result

async def send_broadcast_process(message: str, target_groups: list[str], media_files: list):
    if not message.strip() and not media_files:
        raise HTTPException(status_code=400, detail="Nội dung tin nhắn hoặc file đính kèm không được để trống!")
    
    if not target_groups:
        raise HTTPException(status_code=400, detail="Vui lòng chọn ít nhất 1 nhóm nhận tin!")

    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="BOT_TOKEN chưa được thiết lập!")

    groups_dict = load_json(GROUPS_FILE, {})
    success_group_titles = []
    failed_group_titles = []
    sent_records = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for group_id in target_groups:
            group_title = groups_dict.get(group_id, {}).get("title", f"Nhóm ({group_id})")
            try:
                chat_id = int(group_id)

                if not media_files:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    res = await client.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
                    if res.status_code != 200:
                        res = await client.post(url, json={"chat_id": chat_id, "text": message})
                    
                    if res.status_code == 200:
                        res_data = res.json()
                        msg_id = res_data.get("result", {}).get("message_id")
                        if msg_id:
                            sent_records.append({
                                "chat_id": chat_id,
                                "group_title": group_title,
                                "message_id": msg_id,
                                "revoked": False
                            })
                        success_group_titles.append(group_title)
                    else:
                        failed_group_titles.append(group_title)

                else:
                    group_success = True
                    first_item = True

                    for file_path, filename, content_type in media_files:
                        caption_text = message if first_item else ""
                        first_item = False

                        with open(file_path, "rb") as f:
                            file_bytes = f.read()

                        is_image = content_type.startswith("image/") or filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
                        api_method = "sendPhoto" if is_image else "sendDocument"
                        param_name = "photo" if is_image else "document"

                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{api_method}"
                        data = {"chat_id": str(chat_id)}
                        if caption_text:
                            data["caption"] = caption_text

                        files_payload = {param_name: (filename, file_bytes, content_type or "application/octet-stream")}
                        
                        res = await client.post(url, data=data, files=files_payload)
                        if res.status_code == 200:
                            res_data = res.json()
                            msg_id = res_data.get("result", {}).get("message_id")
                            if msg_id:
                                sent_records.append({
                                    "chat_id": chat_id,
                                    "group_title": group_title,
                                    "message_id": msg_id,
                                    "revoked": False
                                })
                        else:
                            logger.error(f"Lỗi gửi media tới nhóm {group_id}: {res.text}")
                            group_success = False

                    if group_success:
                        success_group_titles.append(group_title)
                    else:
                        failed_group_titles.append(group_title)
                await asyncio.sleep(1.5)

            except Exception as e:
                logger.error(f"Lỗi gửi tin tới nhóm {group_id}: {e}")
                failed_group_titles.append(group_title)


    history = load_json(HISTORY_FILE, [])
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attachment_info = f" [{len(media_files)} đính kèm]" if media_files else ""
    history.append({
        "timestamp": now_str,
        "type": "st_broadcast",
        "message": (message[:80] + ("..." if len(message) > 80 else "")) + attachment_info,
        "total_target": len(target_groups),
        "success_count": len(success_group_titles),
        "failed_count": len(failed_group_titles),
        "success_groups": success_group_titles,
        "failed_groups": failed_group_titles,
        "sent_records": sent_records,
        "revoked": False
    })
    save_json(HISTORY_FILE, history)

    return {
        "status": "completed",
        "success_count": len(success_group_titles),
        "failed_count": len(failed_group_titles),
        "success_groups": success_group_titles,
        "failed_groups": failed_group_titles
    }

class RevokeRequest(BaseModel):
    history_index: int

class SelectiveRevokeRequest(BaseModel):
    history_index: int
    chat_ids: List[int]

# Endpoint THU HỒI TẤT CẢ TIN NHẮN ĐÃ GỬI
@app.post("/api/revoke_broadcast")
async def revoke_broadcast(req: RevokeRequest):
    history = load_json(HISTORY_FILE, [])
    if req.history_index < 0 or req.history_index >= len(history):
        raise HTTPException(status_code=400, detail="Lịch sử phát tin không tồn tại!")

    item = history[req.history_index]
    if item.get("revoked"):
        raise HTTPException(status_code=400, detail="Lượt phát tin này đã được thu hồi trước đó!")

    sent_records = item.get("sent_records", [])
    if not sent_records:
        raise HTTPException(status_code=400, detail="Không tìm thấy ID tin nhắn Telegram để thu hồi!")

    deleted_count = 0
    failed_count = 0

    async with httpx.AsyncClient(timeout=15.0) as client:
        for rec in sent_records:
            chat_id = rec.get("chat_id")
            msg_id = rec.get("message_id")
            if chat_id and msg_id and not rec.get("revoked"):
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
                try:
                    res = await client.post(url, json={"chat_id": str(chat_id), "message_id": msg_id})
                    if res.status_code == 200 and res.json().get("ok"):
                        rec["revoked"] = True
                        deleted_count += 1
                    else:
                        failed_count += 1
                except Exception:
                    failed_count += 1

    item["revoked"] = True
    item["revoked_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_json(HISTORY_FILE, history)

    return {
        "status": "completed",
        "deleted_count": deleted_count,
        "failed_count": failed_count
    }

# Endpoint THU HỒI THEO TỪNG NHÓM ĐƯỢC CHỌN
@app.post("/api/revoke_selective")
async def revoke_selective(req: SelectiveRevokeRequest):
    history = load_json(HISTORY_FILE, [])
    if req.history_index < 0 or req.history_index >= len(history):
        raise HTTPException(status_code=400, detail="Lịch sử phát tin không tồn tại!")

    item = history[req.history_index]
    sent_records = item.get("sent_records", [])

    if not sent_records:
        raise HTTPException(status_code=400, detail="Không tìm thấy ID tin nhắn để thu hồi!")

    target_chat_ids = set(req.chat_ids)
    deleted_count = 0
    failed_count = 0

    async with httpx.AsyncClient(timeout=15.0) as client:
        for rec in sent_records:
            cid = rec.get("chat_id")
            mid = rec.get("message_id")
            if cid in target_chat_ids and not rec.get("revoked"):
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
                try:
                    res = await client.post(url, json={"chat_id": str(cid), "message_id": mid})
                    if res.status_code == 200 and res.json().get("ok"):
                        rec["revoked"] = True
                        deleted_count += 1
                    else:
                        failed_count += 1
                except Exception:
                    failed_count += 1

    if all(r.get("revoked") for r in sent_records):
        item["revoked"] = True
        item["revoked_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_json(HISTORY_FILE, history)

    return {
        "status": "completed",
        "deleted_count": deleted_count,
        "failed_count": failed_count,
        "sent_records": sent_records,
        "item_revoked": item.get("revoked", False)
    }


# ==========================================
# CÁC ENDPOINT ĐỐI SOÁT KHO RAU, DATAPAY & GITHUB SYNC
# ==========================================

@app.get("/api/doi-soat/summary")
async def get_doi_soat_summary():
    """Lấy thống kê tổng quan dữ liệu đối soát theo 5 Step và Datapay."""
    try:
        from doi_soat_engine import get_pipeline_summary
        summary = get_pipeline_summary()
        return {"status": "success", "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/doi-soat/sync")
async def sync_doi_soat_sheet():
    """Kích hoạt đồng bộ Google Sheet Đối Soát Kho Rau tháng 09.2026 vào CSDL SQLite."""
    try:
        from doi_soat_engine import sync_sheet_to_database, get_pipeline_summary
        sync_res = sync_sheet_to_database()
        summary = get_pipeline_summary()
        return {
            "status": "success",
            "sync_result": sync_res,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/doi-soat/datapay")
async def get_datapay_list(period: str = "2026-09"):
    """Lấy danh sách chi tiết số lượng rổ nợ và số tiền bồi hoàn (Datapay) theo từng Siêu thị."""
    try:
        import sqlite3
        from doi_soat_engine import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                d.id_st,
                s.store_name,
                d.period,
                d.basket_code,
                b.basket_name,
                d.missing_qty,
                d.resolved_qty,
                d.net_owe_qty,
                d.unit_price,
                d.total_amount,
                d.responsible_party,
                d.pay_status
            FROM datapay_records d
            LEFT JOIN stores s ON d.id_st = s.id_st
            LEFT JOIN basket_types b ON d.basket_code = b.basket_code
            WHERE d.period = ?
            ORDER BY d.total_amount DESC
        """, (period,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return {"status": "success", "period": period, "total": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/git/push")
async def trigger_git_push(commit_message: Optional[str] = None):
    """Kích hoạt tự động commit và push toàn bộ thay đổi lên GitHub."""
    try:
        from scripts.git_sync import run_git_sync
        success = run_git_sync(commit_msg=commit_message)
        if success:
            return {"status": "success", "message": "Đã commit và push lên GitHub thành công!"}
        else:
            return {"status": "warning", "message": "Đồng bộ hoàn tất hoặc không có thay đổi mới."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi push GitHub: {e}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Khởi chạy Web Dashboard tại http://0.0.0.0:5000 ...")
    uvicorn.run(app, host="0.0.0.0", port=5000)

