import sys
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def generate_st_table_image(id_st: str, items: list, output_path: str):
    headers = [
        "ID ST", "Ngày chuyển", "Chi nhánh chuyển", "Chi nhánh nhận",
        "Mã hàng", "Tên hàng", "ĐVT", "SL chuyển", "Mã phiếu",
        "Trạng thái", "Thời gian tạo", "Classify"
    ]
    col_widths = [65, 95, 160, 160, 120, 260, 50, 75, 95, 100, 130, 180]
    row_height = 36
    
    total_width = sum(col_widths) + 20
    total_height = row_height * (len(items) + 1) + 20
    
    img = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 13)
        font_bold = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font

    # Vẽ Header
    y = 10
    draw.rectangle([10, y, total_width - 10, y + row_height], fill=(240, 242, 245), outline=(200, 200, 200))
    
    x = 15
    for i, h in enumerate(headers):
        draw.text((x, y + 9), h, fill=(0, 0, 0), font=font_bold)
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
            item.get("tg_tao", ""),
            item.get("classify", "")
        ]
        
        x = 15
        for i, val in enumerate(row_data):
            val_str = str(val)
            # Truncate nếu dài quá
            if i in [2, 3] and len(val_str) > 22:
                val_str = val_str[:19] + "..."
            elif i == 5 and len(val_str) > 32:
                val_str = val_str[:29] + "..."
            elif i == 11 and len(val_str) > 24:
                val_str = val_str[:21] + "..."
                
            draw.text((x, y + 8), val_str, fill=(30, 41, 59), font=font)
            x += col_widths[i]
            
        y += row_height

    img.save(output_path)
    print(f"✅ Tạo thành công {output_path}")

sample_items = [
    {
        "id_st": "HLR",
        "ngay_chuyen": "24/07/2026",
        "cn_chuyen": "KFM_HCM_NBE - 222 Lê Văn Lương",
        "cn_nhan": "KHO SEEDLOG ĐỔI TRẢ",
        "ma_hang": "8938505002286",
        "ten_hang": "PMT - MÈ TRẮNG KHÔNG VỎ 100G",
        "dvt": "GÓI",
        "sl_chuyen": "12",
        "ma_phieu": "PT1592649",
        "trang_thai": "Đang chuyển",
        "tg_tao": "22/07/2026 17:30",
        "classify": "Chờ DC nhận hàng"
    }
]

generate_st_table_image("HLR", sample_items, "sample_new_columns.png")
