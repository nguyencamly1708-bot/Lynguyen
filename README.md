# Telegram Bot Python Project

Dự án Telegram Bot hoàn chỉnh được khởi tạo tự động.

## 🚀 Các bước cài đặt và khởi chạy

### Bước 1: Lấy BOT_TOKEN từ Telegram
1. Tìm kiếm và nhắn tin cho **`@BotFather`** trên ứng dụng Telegram.
2. Gửi lệnh `/newbot` và làm theo hướng dẫn để đặt tên cho Bot.
3. BotFather sẽ cấp cho bạn một chuỗi **HTTP API Token** (Ví dụ: `7123456789:AAEF...`).

### Bước 2: Cấu hình Token vào file `.env`
1. Mở file [.env](file:///C:/Users/Admin/.gemini/antigravity/scratch/telegram_bot/.env).
2. Dán mã token của bạn vào sau dấu `=`:
   ```env
   BOT_TOKEN=7123456789:AAEF...
   ```

### Bước 3: Chạy Bot
Mở Terminal tại thư mục này và chạy một trong hai câu lệnh sau:
```bash
.\.venv\Scripts\python.exe bot.py
```
Hoặc dùng `uv`:
```bash
uv run bot.py
```

Khi chạy thành công, Terminal sẽ hiện thông báo:
`🚀 Bot đang chạy và chờ tin nhắn từ Telegram...`
Bây giờ bạn có thể tìm tên Bot của bạn trên Telegram và nhấn `/start` để thử nghiệm!

