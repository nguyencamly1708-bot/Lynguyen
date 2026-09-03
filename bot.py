import json
import logging
import os
import sys
from dotenv import load_dotenv

# Đảm bảo mã hóa UTF-8 cho stdout trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUPS_FILE = "groups.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hàm lưu danh sách nhóm vào file json
def load_groups() -> dict:
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_groups(groups: dict) -> None:
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

# Tự động lưu thông tin Nhóm (Group/Supergroup) khi có sự kiện trong nhóm
async def track_group(update: Update) -> None:
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        chat_id_str = str(chat.id)
        groups = load_groups()
        if chat_id_str not in groups or groups[chat_id_str].get("title") != chat.title:
            groups[chat_id_str] = {
                "title": chat.title,
                "type": chat.type
            }
            save_groups(groups)
            logger.info(f"Đã lưu thông tin nhóm mới: {chat.title} ({chat.id})")

# Xử lý lệnh /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await track_group(update)
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 **Chào {user_name}!**\n\n"
        f"Bot `teamSCM_bot` đã sẵn sàng hoạt động trong nhóm này!\n\n"
        f"📌 Các lệnh có sẵn:\n"
        f"• /start - Khởi động lại Bot\n"
        f"• /help - Xem trợ giúp\n"
        f"• /info - Xem thông tin Chat ID nhóm/cá nhân\n"
        f"• /groups - Danh sách các nhóm Bot đã lưu\n"
        f"• /send_all <nội dung> - Gửi tin nhắn đến TẤT CẢ các nhóm\n"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# Xử lý lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await track_group(update)
    help_text = (
        "💡 **Hướng dẫn gửi tin nhắn nhóm:**\n\n"
        "1. Thêm Bot này `@teamSCM_bot` vào nhóm Telegram của bạn.\n"
        "2. Nhắn lệnh `/start` hoặc tin bất kỳ trong nhóm để Bot nhận diện nhóm.\n"
        "3. Dùng lệnh `/send_all <nội dung>` để gửi tin nhắn đến tất cả các nhóm cùng lúc!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Xử lý lệnh /info
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await track_group(update)
    chat = update.effective_chat
    user = update.effective_user
    info_text = (
        f"📊 **Thông tin Chat:**\n"
        f"• **Loại Chat:** `{chat.type}`\n"
        f"• **Tên:** {chat.title or user.first_name}\n"
        f"• **Chat ID:** `{chat.id}`"
    )
    await update.message.reply_text(info_text, parse_mode="Markdown")

# Xử lý lệnh /groups - Xem danh sách nhóm đã lưu
async def groups_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await track_group(update)
    groups = load_groups()
    if not groups:
        await update.message.reply_text("📂 Bot chưa được thêm vào nhóm nào hoặc chưa ghi nhận nhóm!")
        return

    msg = "📂 **Danh sách nhóm Bot đang tham gia:**\n\n"
    for gid, data in groups.items():
        msg += f"• **{data.get('title')}**: `{gid}`\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# Xử lý lệnh /send_all <nội dung> - Gửi tin nhắn đến tất cả nhóm
async def send_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await track_group(update)
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập nội dung cần gửi. Ví dụ: `/send_all Chào cả nhà!`", parse_mode="Markdown")
        return

    text_to_send = " ".join(context.args)
    groups = load_groups()
    if not groups:
        await update.message.reply_text("❌ Chưa có nhóm nào trong danh sách!")
        return

    success_count = 0
    fail_count = 0
    await update.message.reply_text(f"⏳ Đang gửi tin nhắn đến {len(groups)} nhóm...")

    for gid, data in groups.items():
        try:
            await context.bot.send_message(chat_id=int(gid), text=text_to_send)
            success_count += 1
        except Exception as e:
            logger.error(f"Không thể gửi tới nhóm {gid}: {e}")
            fail_count += 1

    result_text = f"✅ **Hoàn tất gửi tin nhắn!**\n• Thành công: {success_count} nhóm\n• Thất bại: {fail_count} nhóm"
    await update.message.reply_text(result_text, parse_mode="Markdown")

# Xử lý tin nhắn văn bản thông thường
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await track_group(update)
    # Trong nhóm private/cá nhân, bot trả lời tin nhắn
    if update.effective_chat.type == "private":
        user_text = update.message.text
        response_text = f"🤖 Bot nhận được tin nhắn:\n> {user_text}"
        await update.message.reply_text(response_text)

# Xử lý tự động duyệt thành viên mới xin vào nhóm/kênh (Auto Accept Join Request)
from telegram.ext import ChatJoinRequestHandler

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
        logger.info(f"✅ [AUTO ACCEPT] Đã tự động chấp nhận {full_name} (@{user.username or user.id}) vào nhóm '{chat.title}' ({chat.id})")
    except Exception as e:
        logger.error(f"❌ [AUTO ACCEPT FAILED] Lỗi duyệt user {user.id} vào nhóm {chat.id}: {e}")

# Xử lý lỗi nếu có
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Đã xảy ra lỗi:", exc_info=context.error)

def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("❌ ERROR: Bạn chưa dán BOT_TOKEN vào file .env!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("groups", groups_command))
    app.add_handler(CommandHandler("send_all", send_all_command))
    app.add_handler(ChatJoinRequestHandler(auto_approve_join_request))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    app.add_error_handler(error_handler)

    print("🚀 Bot đang chạy (Auto Accept enabled) và sẵn sàng gửi tin nhắn nhóm...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
