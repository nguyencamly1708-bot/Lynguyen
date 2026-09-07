import json

with open("history.json", "r", encoding="utf-8") as f:
    history = json.load(f)

# Giữ lại lịch sử nhưng làm sạch các bản ghi test bị ghi nhầm 71 ST
for item in history:
    if item.get("type") == "sldt":
        msg = item.get("message", "")
        # Lọc bỏ các mục "Bỏ qua / Chưa chọn Nhóm" trong failed_groups
        if "failed_groups" in item:
            item["failed_groups"] = [g for g in item["failed_groups"] if "Bỏ qua / Chưa chọn Nhóm" not in g]
            item["failed_count"] = len(item["failed_groups"])

        # Nếu là bản ghi test cũ có 71 ST
        if "71 ST" in msg or "37 ST" in msg:
            actual_count = item["success_count"] + item["failed_count"]
            item["total_target"] = actual_count if actual_count > 0 else 1
            if actual_count > 0:
                item["message"] = f"📊 Đối soát SLDT [{actual_count} ST đã chọn] + Bảng Ảnh (11 cột)"
            else:
                item["message"] = "📊 Đối soát SLDT [Kiểm tra cấu hình 11 cột - Chế độ gửi tự động: ĐÃ TẮT]"

with open("history.json", "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

print("Đã làm sạch history.json thành công!")
