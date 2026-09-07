import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from PIL import Image, ImageDraw, ImageFont

sample_vgp_items = [
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938551363041', 'ten_hang': 'MÊ GẠO - GẠO ĐÀI THƠM TÚI 5KG', 'dvt': 'TÚI', 'sl_chuyen': '11', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938530115036', 'ten_hang': 'HOME RICE - GẠO CỰ GIẢI 5KG', 'dvt': 'TÚI', 'sl_chuyen': '5', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938551363003', 'ten_hang': 'MÊ GẠO - GẠO THƠM ĐẶC SẢN ST25 TÚI 5KG', 'dvt': 'TÚI', 'sl_chuyen': '3', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938509043407', 'ten_hang': 'VINH HIỂN - GẠO LỨT THƠM ST25 TÚI 1KG', 'dvt': 'TÚI', 'sl_chuyen': '1', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938526893153', 'ten_hang': 'KIM THIÊN LỘC - GẠO TẤM THƠM ST25 TÚI 1KG', 'dvt': 'TÚI', 'sl_chuyen': '1', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938509043315', 'ten_hang': 'VINH HIỂN - GẠO LỨT ĐỎ TÚI 1KG', 'dvt': 'TÚI', 'sl_chuyen': '1', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938516870300', 'ten_hang': 'NEPTUNE - GẠO THƠM DẺO ĐẶC BIỆT ST25+ TÚI 5KG', 'dvt': 'TÚI', 'sl_chuyen': '2', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8936238480197', 'ten_hang': 'NUFFAM - BÚN TƯƠI KHÔ 400G', 'dvt': 'GÓI', 'sl_chuyen': '2', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938505002620', 'ten_hang': 'PMT - ĐẬU XANH CÀ 250G', 'dvt': 'GÓI', 'sl_chuyen': '1', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938515083152', 'ten_hang': 'PHƯƠNG NGUYÊN - BÁNH TRÁNG CUỐN MÈ ĐEN GÓI 200G', 'dvt': 'GÓI', 'sl_chuyen': '1', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938509043407', 'ten_hang': 'VINH HIỂN - GẠO LỨT THƠM ST25 TÚI 1KG', 'dvt': 'TÚI', 'sl_chuyen': '3', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'},
    {'id_st': 'VGP', 'ngay_chuyen': '02/09/2026', 'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park', 'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ', 'ma_hang': '8938551363003', 'ten_hang': 'MÊ GẠO - GẠO THƠM ĐẶC SẢN ST25 TÚI 5KG', 'dvt': 'TÚI', 'sl_chuyen': '5', 'ma_chuyen_hang': 'PT1751492', 'trang_thai': 'Đang chuyển', 'tg_tao': '01/09/2026 18:01'}
]

def generate_hinh2_style_table_image(id_st: str, items: list, output_path: str):
    headers = [
        "ID ST", "Ngày chuyển hàng", "Chi nhánh chuyển", "Chi nhánh nhận",
        "Mã hàng", "Tên hàng", "Đơn vị tính", "Số lượng chuyển",
        "Mã chuyển hàng", "Trạng thái", "Thời gian tạo"
    ]

    try:
        font_header = ImageFont.truetype("arialbd.ttf", 13)
        font_row = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_header = ImageFont.load_default()
        font_row = font_header

    min_widths = [60, 115, 230, 155, 110, 270, 75, 100, 105, 95, 115]
    col_widths = list(min_widths)

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
            item.get("ma_chuyen_hang", item.get("ma_phieu", "")),
            item.get("trang_thai", ""),
            item.get("tg_tao", "")
        ]
        for i, val in enumerate(row_vals):
            bbox = font_row.getbbox(str(val))
            w = (bbox[2] - bbox[0]) + 20
            if w > col_widths[i]:
                col_widths[i] = w

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

    img = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    header_bg_color = (244, 184, 188)
    grid_line_color = (215, 220, 225)
    header_text_color = (17, 24, 39)
    body_text_color = (17, 24, 39)

    header_y = margin_y
    draw.rectangle(
        [margin_x, header_y, margin_x + table_width, header_y + header_height],
        fill=header_bg_color
    )

    curr_x = margin_x
    for i, h in enumerate(headers):
        w = col_widths[i]
        draw.line([(curr_x, header_y), (curr_x, header_y + header_height)], fill=grid_line_color, width=1)
        
        bbox = font_header.getbbox(h)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_y = header_y + (header_height - text_h) // 2 - 2
        
        if i == 7: # Cột Số lượng chuyển căn phải
            text_x = curr_x + w - text_w - 8
        elif i in [0, 1, 6, 8, 10]: # ID ST, Ngày, ĐVT, Mã PT, Giờ tạo căn giữa
            text_x = curr_x + (w - text_w) // 2
        else:
            text_x = curr_x + 8
            
        draw.text((text_x, text_y), h, fill=header_text_color, font=font_header)
        curr_x += w
    draw.line([(curr_x, header_y), (curr_x, header_y + header_height)], fill=grid_line_color, width=1)

    curr_y = header_y + header_height
    for idx, item in enumerate(items):
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
            item.get("ma_chuyen_hang", item.get("ma_phieu", "")),
            item.get("trang_thai", ""),
            item.get("tg_tao", "")
        ]

        curr_x = margin_x
        for i, val in enumerate(row_vals):
            w = col_widths[i]
            draw.line([(curr_x, curr_y), (curr_x, curr_y + row_height)], fill=grid_line_color, width=1)

            val_str = str(val) if val is not None else ""
            bbox = font_row.getbbox(val_str)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_y = curr_y + (row_height - text_h) // 2 - 2

            if i == 7:
                text_x = curr_x + w - text_w - 8
            elif i in [0, 1, 6, 8, 10]:
                text_x = curr_x + (w - text_w) // 2
            else:
                text_x = curr_x + 8

            draw.text((text_x, text_y), val_str, fill=body_text_color, font=font_row)
            curr_x += w

        draw.line([(curr_x, curr_y), (curr_x, curr_y + row_height)], fill=grid_line_color, width=1)
        curr_y += row_height

    draw.line([(margin_x, curr_y), (margin_x + table_width, curr_y)], fill=grid_line_color, width=1)
    draw.rectangle(
        [margin_x, header_y, margin_x + table_width, curr_y],
        outline=(180, 190, 200),
        width=1
    )

    img.save(output_path, quality=95)
    return output_path

if __name__ == "__main__":
    out_test = "h:/My Drive/Lynguyen/test_hinh2_11cols_output.png"
    generate_hinh2_style_table_image("VGP", sample_vgp_items, out_test)
    print(f"Generated 11-column test image at: {out_test}")
