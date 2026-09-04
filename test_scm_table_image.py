import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

def generate_scm_table_image(id_st: str, items: list, output_path: str):
    # Style giống y hệt ảnh 3 "Đối soát SCM":
    # Header: "Đối soát SCM" (chữ xanh lá trên nền tối)
    # Cột: Cam nổi bật (#EA580C / #F97316), chữ trắng
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

    # Tính độ rộng cột tự co dãn dựa trên nội dung thực tế
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
    # Margin hai bên
    margin_x = 16
    margin_y = 16
    title_height = 48
    header_height = 36
    row_height = 34

    total_width = table_width + (margin_x * 2)
    total_height = margin_y + title_height + header_height + (len(items) * row_height) + margin_y

    # Tạo canvas nền tối hiện đại (dark theme giống giao diện Telegram trong ảnh 3)
    img = Image.new("RGB", (total_width, total_height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # 1. Vẽ Tiêu đề "Đối soát SCM"
    draw.text((margin_x + 4, margin_y + 8), "Đối soát SCM", fill=(34, 197, 94), font=font_title)

    # 2. Vẽ Header bảng (Màu Cam #EA580C)
    header_y = margin_y + title_height
    draw.rectangle(
        [margin_x, header_y, margin_x + table_width, header_y + header_height],
        fill=(234, 88, 12)
    )

    curr_x = margin_x
    for i, h in enumerate(headers):
        draw.text((curr_x + 10, header_y + 9), h, fill=(255, 255, 255), font=font_header)
        curr_x += col_widths[i]

    # 3. Vẽ các dòng dữ liệu (Dòng trắng và dòng xám nhẹ zebra)
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
            # Căn giữa ĐVT và SL chuyển, căn trái Tên hàng
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
    print(f"Created test table image: {output_path}")

sample_items = [
    {"id_st": "AV4", "ma_phieu": "PT1583250", "ma_hang": "1100942", "ten_hang": "BƠ BOOTH", "dvt": "KG", "sl_chuyen": "3,00"},
    {"id_st": "AV4", "ma_phieu": "PT1583250", "ma_hang": "1101062", "ten_hang": "CHUỐI LABA ĐÀ LẠT", "dvt": "KG", "sl_chuyen": "20,00"},
    {"id_st": "AV4", "ma_phieu": "PT1583250", "ma_hang": "1101079", "ten_hang": "BƠ 034", "dvt": "KG", "sl_chuyen": "6,10"},
    {"id_st": "AV4", "ma_phieu": "PT1583250", "ma_hang": "1101094", "ten_hang": "MÍT GIỐNG THÁI CẮT MIẾNG", "dvt": "KG", "sl_chuyen": "3,00"},
    {"id_st": "AV4", "ma_phieu": "PT1583250", "ma_hang": "1101366", "ten_hang": "BÔNG CẢI XANH ĐÀ LẠT (KG)", "dvt": "KG", "sl_chuyen": "8,00"},
    {"id_st": "AV4", "ma_phieu": "PT1583250", "ma_hang": "1101941", "ten_hang": "DƯA LƯỚI VỎ VÀNG RUỘT CAM", "dvt": "KG", "sl_chuyen": "12,60"},
]

generate_scm_table_image("AV4", sample_items, "sample_doi_soat_scm.png")
