import sys
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def generate_st_table_image(id_st: str, items: list, output_path: str):
    # Cấu hình bảng
    headers = ["ID ST", "Mã phiếu", "Mã hàng", "Tên sản phẩm", "ĐVT", "SL", "Classify"]
    col_widths = [80, 110, 130, 360, 60, 50, 260]
    row_height = 36
    padding = 12
    
    total_width = sum(col_widths)
    total_height = row_height * (len(items) + 1) + 20
    
    # Tạo Canvas trắng/xám hiện đại
    img = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font

    # Vẽ Header
    y = 10
    draw.rectangle([0, y, total_width, y + row_height], fill=(240, 242, 245), outline=(200, 200, 200))
    
    x = 10
    for i, h in enumerate(headers):
        draw.text((x, y + 10), h, fill=(0, 0, 0), font=font_bold)
        x += col_widths[i]
        
    # Vẽ các dòng dữ liệu
    y += row_height
    for idx, item in enumerate(items):
        bg_color = (255, 255, 255) if idx % 2 == 0 else (248, 250, 252)
        draw.rectangle([0, y, total_width, y + row_height], fill=bg_color, outline=(226, 232, 240))
        
        row_data = [
            item.get("id_st", id_st),
            item.get("ma_phieu", ""),
            item.get("ma_hang", ""),
            item.get("ten_hang", ""),
            item.get("dvt", ""),
            str(item.get("sl", "")),
            item.get("classify", "")
        ]
        
        x = 10
        for i, val in enumerate(row_data):
            # Cắt ngắn nếu tên sản phẩm quá dài
            val_str = str(val)
            if i == 3 and len(val_str) > 38:
                val_str = val_str[:35] + "..."
            elif i == 6 and len(val_str) > 30:
                val_str = val_str[:27] + "..."
                
            draw.text((x, y + 9), val_str, fill=(30, 41, 59), font=font)
            x += col_widths[i]
            
        y += row_height

    img.save(output_path)
    print(f"✅ Đã tạo bảng ảnh thành công tại: {output_path}")

sample_items = [
    {"id_st": "A120", "ma_phieu": "PT1583250", "ma_hang": "8934673323512", "ten_hang": "VINAMILK - SỮA PROBI HƯƠNG DỪA 5*65ML", "dvt": "LỐC", "sl": "10", "classify": "Chờ DC nhận hàng"},
    {"id_st": "A120", "ma_phieu": "PT1583250", "ma_hang": "8935217410507", "ten_hang": "TH TRUE MILK - SC MEN SỐNG VIỆT QUẤT TỰ NHIÊN 100G", "dvt": "HỘP", "sl": "16", "classify": "Chờ DC nhận hàng"}
]

generate_st_table_image("A120", sample_items, "sample_table.png")
