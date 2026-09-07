import sys, os
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, r"h:\My Drive\Lynguyen")
from server import generate_st_table_image

sample_items = [
    {
        'id_st': 'VGP',
        'ngay_chuyen': '02/09/2026',
        'cn_chuyen': 'KFM_HCM_TDU - S06.06 Vinhomes Grand Park',
        'cn_nhan': 'KHO SEEDLOG ĐỔI TRẢ',
        'ma_hang': '8938551363041',
        'ten_hang': 'MÊ GẠO - GẠO ĐÀI THƠM TÚI 5KG',
        'dvt': 'TÚI',
        'sl_chuyen': '11',
        'sl_nhan': '11',
        'sl_nhan_ht': '',
        'ma_chuyen_hang': 'PT1751492',
        'trang_thai': 'Đang chuyển',
        'tg_tao': '01/09/2026 18:01'
    }
]

out_p = "h:/My Drive/Lynguyen/test_server_11cols_out.png"
generate_st_table_image("VGP", sample_items, out_p)
print(f"OK: Bang anh 11 cot tao thanh cong tai: {out_p}")
