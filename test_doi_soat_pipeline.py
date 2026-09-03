import sys
import io
import os
import sqlite3

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from doi_soat_engine import (
    sync_sheet_to_database,
    get_pipeline_summary,
    DB_PATH
)

def run_tests():
    print("=" * 60)
    print("BẮT ĐẦU KIỂM THỬ PIPELINE ĐỐI SOÁT & DATAPAY (THÁNG 09.2026)")
    print("=" * 60)

    # Test 1: Đồng bộ Sheet
    print("\n[TEST 1] Đồng bộ dữ liệu từ Google Sheets vào SQLite...")
    sync_res = sync_sheet_to_database()
    assert sync_res["status"] == "success", "Lỗi sync_sheet_to_database!"
    print(f"-> THÀNH CÔNG: Đã nạp {sync_res['total_rows']} dòng dữ liệu.")

    # Test 2: Kiểm tra tổng quan 5 Step
    print("\n[TEST 2] Kiểm tra phân loại 5 Step & Trách nhiệm lỗi...")
    summary = get_pipeline_summary()
    steps = summary["steps"]
    parties = summary["responsible_parties"]
    print("-> Phân bố theo Step:")
    for k, v in steps.items():
        print(f"   + {k}: {v}")
    print("-> Phân bố theo Bên chịu lỗi:")
    for k, v in parties.items():
        print(f"   + {k}: {v}")
    assert sum(steps.values()) > 0, "Không có dữ liệu Step!"

    # Test 3: Kiểm tra tính toán Datapay
    print("\n[TEST 3] Kiểm tra tính toán số liệu Datapay kỳ 2026-09...")
    datapay = summary["datapay"]
    print(f"   + Số Siêu thị có phát sinh nợ đền bù: {datapay['total_stores_owe']}")
    print(f"   + Tổng số lượng rổ nợ thực tế: {datapay['total_net_owe_baskets']}")
    print(f"   + Tổng thành tiền Datapay: {datapay['total_datapay_amount']:,.0f} VNĐ")
    assert datapay["total_stores_owe"] > 0, "Không có dữ liệu Datapay!"

    # Test 4: Truy vấn top 5 Siêu thị nợ bồi hoàn cao nhất
    print("\n[TEST 4] Top 5 Siêu thị có số lượng nợ thùng rổ cao nhất:")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            d.id_st,
            s.store_name,
            SUM(d.net_owe_qty) as total_net_owe,
            SUM(d.total_amount) as total_amount
        FROM datapay_records d
        LEFT JOIN stores s ON d.id_st = s.id_st
        GROUP BY d.id_st
        ORDER BY total_amount DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    for idx, r in enumerate(rows, 1):
        print(f"   {idx}. ST [{r['id_st']}]: {r['store_name']} -> Nợ: {r['total_net_owe']} rổ | Tiền: {r['total_amount']:,.0f} VNĐ")
    conn.close()

    print("\n" + "=" * 60)
    print("TẤT CẢ CÁC BÀI KIỂM THỬ ĐÃ ĐẠT KẾT QUẢ XUẤT SẮC (PASS)!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
