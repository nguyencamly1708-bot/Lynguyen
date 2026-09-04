# QUY TẮC AN TOÀN TUYỆT ĐỐI KHI XỬ LÝ VÀ THU HỒI TIN NHẮN TELEGRAM

## 1. Nguyên Tắc Bất Di Bất Dịch
- **TUYỆT ĐỐI KHÔNG BAO GIỜ** được viết script hoặc chạy lệnh quét tin nhắn theo khoảng thời gian (timestamp) hoặc theo `sender_id` / tài khoản người dùng để xóa hàng loạt.
- Bất kỳ thao tác xóa/thu hồi tin nhắn nào (`revoke=True` hoặc `deleteMessage`) **BẮT BUỘC PHẢI DỰA TRÊN DANH SÁCH CỤ THỂ CỦA CÁC `message_id`** đã được hệ thống ghi nhận khi phát tin.
- Tuyệt đối không xóa bất kỳ tin nhắn nào không nằm trong danh sách `message_id` được ghi nhận.

## 2. Quy Trình Lưu Trữ Khi Phát Tin
- Khi bất kỳ đợt phát tin nào diễn ra (dù qua tài khoản cá nhân `@JinLi072` hay qua Bot Token):
  1. Ghi nhận tức thời từng cặp `(chat_id, message_id, group_title)` vào danh sách `sent_records`.
  2. Lưu danh sách này vào `history.json` và tệp `last_broadcast_sent.json`.

## 3. Quy Trình Thu Hồi Tin Nhắn
- Khi người dùng bấm nút thu hồi trên Dashboard hoặc có yêu cầu thu hồi:
  1. Chỉ đọc danh sách `sent_records` từ đợt phát tin đó.
  2. Duyệt qua từng `message_id` cụ thể trong danh sách và gọi lệnh xóa `revoke=True`.
  3. Cập nhật trạng thái `revoked = True` để tránh xóa trùng lặp.
  4. Báo cáo chính xác số lượng tin nhắn đã xóa thành công.
