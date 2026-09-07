import sys
import os
from PIL import Image, ImageDraw, ImageFont

def generate_hinh2_style_table_image(id_st: str, items: list, output_path: str):
    headers = [
        "ID ST", "Ngày chuyển hàng", "Chi nhánh chuyển", "Chi nhánh nhận",
        "Mã hàng", "Tên hàng", "Đơn vị tính", "Số lượng chuyển",
        "Số lượng nhận", "SL nhận (Hệ thống)", "Mã chuyển hàng",
        "Trạng thái", "Thời gian tạo"
    ]

    # Cố gắng tải font chữ sắc nét
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 13)
        font_row = ImageFont.truetype("arial.ttf", 13)
        font_row_bold = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font_header = ImageFont.load_default()
        font_row = font_header
        font_row_bold = font_header

    # Độ rộng tối thiểu cho từng cột (pixel)
    min_widths = [60, 115, 230, 155, 110, 270, 75, 95, 90, 120, 105, 95, 115]
    col_widths = list(min_widths)

    # Tính độ rộng động dựa trên nội dung thực tế
    for item in items:
        row_vals = [
            item.get("id_st", id_st),
            item.get("ngay_chuyen", ""),
            item.get("cn_chuyen", ""),
            item.get("cn_nhan", ""),
            item.get("ma_hang", ""),
            item.get("ten_hang", ""),
            item.get("dvt", ""),
            str(item.get("sl_chuyen", "")),
            str(item.get("sl_nhan", "")),
            str(item.get("sl_nhan_ht", "")),
            item.get("ma_chuyen_hang", item.get("ma_phieu", "")),
            item.get("trang_thai", ""),
            item.get("tg_tao", "")
        ]
        for i, val in enumerate(row_vals):
            bbox = font_row.getbbox(str(val))
            w = (bbox[2] - bbox[0]) + 20
            if w > col_widths[i]:
                col_widths[i] = w

    # Kiểm tra header width
    for i, h in enumerate(headers):
        bbox = font_header.getbbox(h)
        w = (bbox[2] - bbox[0]) + 24
        if w > col_widths[i]:
            col_widths[i] = w

    table_width = sum(col_widths)
    margin_x = 4
    margin_y = 4
    header_height = 34
    row_height = 28

    total_width = table_width + (margin_x * 2)
    total_height = (margin_y * 2) + header_height + (len(items) * row_height)

    # Nền bảng trắng tinh như Google Sheets trong Hình 2
    img = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 1. Vẽ Header màu Hồng Pastel / Salmon Pink chuẩn Hình 2 (#F3B8BC)
    header_bg_color = (244, 184, 188)
    grid_line_color = (215, 220, 225)
    header_text_color = (17, 24, 39)
    body_text_color = (17, 24, 39)

    header_y = margin_y
    draw.rectangle(
        [margin_x, header_y, margin_x + table_width, header_y + header_height],
        fill=header_bg_color
    )

    # Vẽ chữ và vạch chia cột cho Header
    curr_x = margin_x
    for i, h in enumerate(headers):
        w = col_widths[i]
        # Vạch kẻ dọc header
        draw.line([(curr_x, header_y), (curr_x, header_y + header_height)], fill=grid_line_color, width=1)
        
        # Căn chỉnh text header (cột số căn phải, cột khác căn trái hoặc giữa)
        bbox = font_header.getbbox(h)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_y = header_y + (header_height - text_h) // 2 - 2
        
        if i in [7, 8, 9]: # Các cột số lượng
            text_x = curr_x + w - text_w - 8
        elif i in [0, 1, 6, 10, 12]: # ID, Ngày, ĐVT, Mã PT, Giờ
            text_x = curr_x + (w - text_w) // 2
        else:
            text_x = curr_x + 8
            
        draw.text((text_x, text_y), h, fill=header_text_color, font=font_header)
        curr_x += w
    # Vạch cuối cùng của header
    draw.line([(curr_x, header_y), (curr_x, header_y + header_height)], fill=grid_line_color, width=1)

    # 2. Vẽ từng dòng dữ liệu (Nền trắng, viền lưới kẻ ô rõ ràng)
    curr_y = header_y + header_height
    for idx, item in enumerate(items):
        # Đường kẻ ngang trên mỗi dòng
        draw.line([(margin_x, curr_y), (margin_x + table_width, curr_y)], fill=grid_line_color, width=1)

        row_vals = [
            item.get("id_st", id_st),
            item.get("ngay_chuyen", ""),
            item.get("cn_chuyen", ""),
            item.get("cn_nhan", ""),
            item.get("ma_hang", ""),
            item.get("ten_hang", ""),
            item.get("dvt", ""),
            str(item.get("sl_chuyen", "")),
            str(item.get("sl_nhan", "")),
            str(item.get("sl_nhan_ht", "")),
            item.get("ma_chuyen_hang", item.get("ma_phieu", "")),
            item.get("trang_thai", ""),
            item.get("tg_tao", "")
        ]

        curr_x = margin_x
        for i, val in enumerate(row_vals):
            w = col_widths[i]
            # Vạch kẻ dọc từng ô
            draw.line([(curr_x, curr_y), (curr_x, curr_y + row_height)], fill=grid_line_color, width=1)

            val_str = str(val) if val is not None else ""
            bbox = font_row.getbbox(val_str)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_y = curr_y + (row_height - text_h) // 2 - 2

            # Căn lề từng cột
            if i in [7, 8, 9]: # Số lượng căn phải
                text_x = curr_x + w - text_w - 8
            elif i in [0, 1, 6, 10, 12]: # ID, Ngày, ĐVT, Mã PT, Giờ tạo căn giữa
                text_x = curr_x + (w - text_w) // 2
            else: # Tên hàng, chi nhánh căn trái
                text_x = curr_x + 8

            draw.text((text_x, text_y), val_str, fill=body_text_color, font=font_row)
            curr_x += w

        # Vạch kẻ dọc cuối cùng của dòng
        draw.line([(curr_x, curr_y), (curr_x, curr_y + row_height)], fill=grid_line_color, width=1)
        curr_y += row_height

    # Kẻ ngang đáy bảng
    draw.line([(margin_x, curr_y), (margin_x + table_width, curr_y)], fill=grid_line_color, width=1)
    
    # Viền bao quanh ngoài bảng
    draw.rectangle(
        [margin_x, header_y, margin_x + table_width, curr_y],
        outline=(180, 190, 200),
        width=1
    )

    img.save(output_path, quality=95)
    return output_path

if __name__ == "__main__":
    # Test với dữ liệu VGP thực tế
    from test_vgp_extract import vgp_rows
    out_test = "h:/My Drive/Lynguyen/test_hinh2_output.png"
    generate_hinh2_style_table_image("VGP", vgp_rows, out_test)
    print(f"Generated test image at: {out_test}")
