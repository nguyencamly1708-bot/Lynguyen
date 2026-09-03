import sys
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def generate_st_table_image(id_st: str, items: list, output_path: str):
    headers = [
        "ID ST", "Ngày chuyển", "Chi nhánh chuyển", "Chi nhánh nhận",
        "Mã hàng", "Tên hàng", "ĐVT", "SL chuyển", "Mã phiếu",
        "Trạng thái", "Thời gian tạo"
    ]
    
    # 1. Tính toán chiều rộng cột tự động dựa trên độ dài văn bản thực tế
    try:
        font = ImageFont.truetype("arial.ttf", 13)
        font_bold = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font

    # Chiều rộng tối thiểu cho từng cột
    min_widths = [65, 100, 280, 220, 125, 450, 55, 80, 100, 110, 140]
    col_widths = list(min_widths)

    for item in items:
        row_data = [
            item.get("id_st", id_st),
            item.get("ngay_chuyen", ""),
            item.get("cn_chuyen", ""),
            item.get("cn_nhan", ""),
            item.get("ma_hang", ""),
            item.get("ten_hang", ""),
            item.get("dvt", ""),
            str(item.get("sl_chuyen", "")),
            item.get("ma_phieu", ""),
            item.get("trang_thai", ""),
            item.get("tg_tao", "")
        ]
        for i, val in enumerate(row_data):
            # Tính độ dài text thực tế bằng bbox
            text_str = str(val)
            bbox = font.getbbox(text_str)
            text_w = bbox[2] - bbox[0] + 30 # Cộng margin
            if text_w > col_widths[i]:
                col_widths[i] = text_w

    row_height = 38
    total_width = sum(col_widths) + 20
    total_height = row_height * (len(items) + 1) + 20
    
    img = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Vẽ Header
    y = 10
    draw.rectangle([10, y, total_width - 10, y + row_height], fill=(240, 242, 245), outline=(200, 200, 200))
    
    x = 15
    for i, h in enumerate(headers):
        draw.text((x, y + 10), h, fill=(0, 0, 0), font=font_bold)
        x += col_widths[i]
        
    y += row_height
    for idx, item in enumerate(items):
        bg_color = (255, 255, 255) if idx % 2 == 0 else (248, 250, 252)
        draw.rectangle([10, y, total_width - 10, y + row_height], fill=bg_color, outline=(226, 232, 240))
        
        row_data = [
            item.get("id_st", id_st),
            item.get("ngay_chuyen", ""),
            item.get("cn_chuyen", ""),
            item.get("cn_nhan", ""),
            item.get("ma_hang", ""),
            item.get("ten_hang", ""),
            item.get("dvt", ""),
            str(item.get("sl_chuyen", "")),
            item.get("ma_phieu", ""),
            item.get("trang_thai", ""),
            item.get("tg_tao", "")
        ]
        
        x = 15
        for i, val in enumerate(row_data):
            # Không cắt bớt ký tự nào hết - Giữ nguyên 100% văn bản!
            draw.text((x, y + 9), str(val), fill=(30, 41, 59), font=font)
            x += col_widths[i]
            
        y += row_height

    img.save(output_path)
    print(f"✅ Đã tạo bảng ảnh đầy đủ thông tin thành công: {output_path} (Kích thước width={total_width}px)")

sample_items = [
    {
        "id_st": "A144",
        "ngay_chuyen": "30/07/2026",
        "cn_chuyen": "KFM_HCM_Q07 - A01-06 ĐẠI LỘ NGUYỄN VĂN LINH",
        "cn_nhan": "KHO SEEDLOG ĐỔI TRẢ TẬN NƠI",
        "ma_hang": "8934563304157",
        "ten_hang": "ACECOOK - MIẾN PHÚ HƯƠNG LẨU THÁI NẤM TÔM TÚI 5 GÓI 60G",
        "dvt": "GÓI",
        "sl_chuyen": "12",
        "ma_phieu": "PT1588355",
        "trang_thai": "Đang chuyển",
        "tg_tao": "29/07/2026 23:18"
    }
]

generate_st_table_image("A144", sample_items, "sample_full_text.png")
