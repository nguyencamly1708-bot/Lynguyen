import csv
import io
import os
import sys
import sqlite3
import datetime
import httpx
from typing import Dict, List, Any, Optional

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# CẤU HÌNH GOOGLE SHEET ĐỐI SOÁT KHO RAU THÁNG 09.2026
SHEET_ID = "1GcAQs5mEtm6Itp5c6K8OgsEPhFxBUeYModTm6yb0efY"
SHEET_GID = "0"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doi_soat.db")

# DANH MỤC THÙNG RỔ & ĐƠN GIÁ BỒI HOÀN QUY ƯỚC (VNĐ)
DEFAULT_BASKET_PRICES = {
    "CC00381": {"name": "Tote đỏ bánh tươi", "unit_price": 120000},
    "CC00360": {"name": "Rổ đen xếp chồng quai đỏ", "unit_price": 85000},
    "CC00359": {"name": "Seedlog - Thùng tote xanh lá, xanh dương không đục lỗ", "unit_price": 110000},
}

def init_database(db_path: str = DB_PATH):
    """Khởi tạo cấu trúc cơ sở dữ liệu SQLite theo thiết kế ERD."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Bảng Siêu Thị (STORES)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id_st TEXT PRIMARY KEY,
            store_name TEXT,
            telegram_group_id TEXT,
            sm_mentions TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Bảng Danh Mục Thùng Rổ (BASKET_TYPES)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS basket_types (
            basket_code TEXT PRIMARY KEY,
            basket_name TEXT,
            unit_price REAL DEFAULT 0.0
        )
    """)

    # 3. Bảng Chi Tiết Đối Soát (DOI_SOAT_RECORDS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doi_soat_records (
            record_id TEXT PRIMARY KEY,
            transfer_date TEXT,
            source_id TEXT,
            source_name TEXT,
            receiver_name TEXT,
            id_st TEXT,
            basket_code TEXT,
            basket_name TEXT,
            qty_sent INTEGER,
            qty_received INTEGER,
            diff_qty INTEGER,
            pt_code TEXT,
            trip_code TEXT,
            basket_id TEXT,
            to_code TEXT,
            return_st_qty INTEGER,
            cxd_diff_qty INTEGER,
            pt_return_st TEXT,
            pt_return_dc TEXT,
            pt_extra TEXT,
            note1 TEXT,
            error_type TEXT,
            store_fault TEXT,
            dc_fault TEXT,
            process_status TEXT,
            camera_link TEXT,
            timeline TEXT,
            dc_confirm TEXT,
            dc_note TEXT,
            kfm_status TEXT,
            kfm_note TEXT,
            step INTEGER DEFAULT 1,
            responsible_party TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Bảng Dữ Liệu Quyết Toán / Bồi Hoàn (DATAPAY_RECORDS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datapay_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_st TEXT,
            period TEXT,
            basket_code TEXT,
            missing_qty INTEGER DEFAULT 0,
            resolved_qty INTEGER DEFAULT 0,
            net_owe_qty INTEGER DEFAULT 0,
            unit_price REAL DEFAULT 0.0,
            total_amount REAL DEFAULT 0.0,
            responsible_party TEXT,
            pay_status TEXT DEFAULT 'Chờ quyết toán',
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_st) REFERENCES stores (id_st)
        )
    """)

    # 5. Bảng Lịch Sử Đồng Bộ (SYNC_LOGS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_rows INTEGER,
            new_rows INTEGER,
            updated_rows INTEGER,
            status TEXT,
            message TEXT
        )
    """)

    # Nạp dữ liệu danh mục rổ mặc định nếu chưa có
    for code, info in DEFAULT_BASKET_PRICES.items():
        cursor.execute("""
            INSERT OR IGNORE INTO basket_types (basket_code, basket_name, unit_price)
            VALUES (?, ?, ?)
        """, (code, info["name"], info["unit_price"]))

    conn.commit()
    conn.close()
    return True


def fetch_sheet_raw_csv() -> List[List[str]]:
    """Tải và parse toàn bộ dữ liệu từ Google Sheet dưới dạng danh sách dòng."""
    res = httpx.get(SHEET_CSV_URL, timeout=40.0, follow_redirects=True)
    if res.status_code != 200:
        raise Exception(f"Không thể kết nối Google Sheets! HTTP Status: {res.status_code}")
    
    content = res.content.decode("utf-8-sig", errors="ignore")
    rows = list(csv.reader(io.StringIO(content)))
    if len(rows) < 10:
        raise Exception("Google Sheets rỗng hoặc không đúng định dạng!")
    
    return rows


def parse_and_classify_records(rows: List[List[str]]) -> List[Dict[str, Any]]:
    """
    Phân tích 31 cột của Google Sheet, xác định Step quy trình và Phân định trách nhiệm:
    - Step 1: Chênh lệch phát sinh
    - Step 2: Phân loại nguyên nhân lỗi (Siêu thị vs Kho DC)
    - Step 3: Đã lập phiếu xử lý / tính Datapay
    - Step 4: DC xác nhận
    - Step 5: KFM thông tin Hoàn thành (Done)
    """
    records = []
    # Dữ liệu bắt đầu từ dòng 10 (index 9)
    data_rows = rows[9:]

    for idx, r in enumerate(data_rows):
        if not r or len(r) < 10:
            continue
        
        # Bỏ qua dòng tiêu đề nếu bị lặp
        if r[0].strip() == "Ngày chuyển hàng":
            continue

        transfer_date = r[0].strip() if len(r) > 0 else ""
        source_id = r[1].strip() if len(r) > 1 else ""
        source_name = r[2].strip() if len(r) > 2 else ""
        receiver_name = r[3].strip() if len(r) > 3 else ""
        id_st = r[4].strip() if len(r) > 4 else "Khác"
        basket_code = r[5].strip() if len(r) > 5 else ""
        basket_name = r[6].strip() if len(r) > 6 else ""
        
        try:
            qty_sent = int(r[7].strip()) if len(r) > 7 and r[7].strip() else 0
        except ValueError:
            qty_sent = 0
            
        try:
            qty_received = int(r[8].strip()) if len(r) > 8 and r[8].strip() else 0
        except ValueError:
            qty_received = 0

        try:
            diff_qty = int(r[9].strip()) if len(r) > 9 and r[9].strip() else (qty_received - qty_sent)
        except ValueError:
            diff_qty = qty_received - qty_sent

        pt_code = r[10].strip() if len(r) > 10 else ""
        trip_code = r[11].strip() if len(r) > 11 else ""
        basket_id = r[12].strip() if len(r) > 12 else ""
        record_unique_id = r[13].strip() if len(r) > 13 and r[13].strip() else f"{pt_code}_{basket_code}_{idx}"
        to_code = r[14].strip() if len(r) > 14 else ""
        
        try:
            return_st_qty = int(r[15].strip()) if len(r) > 15 and r[15].strip() else 0
        except ValueError:
            return_st_qty = 0

        try:
            cxd_diff_qty = int(r[16].strip()) if len(r) > 16 and r[16].strip() else 0
        except ValueError:
            cxd_diff_qty = 0

        pt_return_st = r[17].strip() if len(r) > 17 else ""
        pt_return_dc = r[18].strip() if len(r) > 18 else ""
        pt_extra = r[19].strip() if len(r) > 19 else ""
        note1 = r[20].strip() if len(r) > 20 else ""
        error_type = r[21].strip() if len(r) > 21 else ""
        store_fault = r[22].strip() if len(r) > 22 else ""
        dc_fault = r[23].strip() if len(r) > 23 else ""
        process_status = r[24].strip() if len(r) > 24 else ""
        camera_link = r[25].strip() if len(r) > 25 else ""
        timeline = r[26].strip() if len(r) > 26 else ""
        dc_confirm = r[27].strip() if len(r) > 27 else ""
        dc_note = r[28].strip() if len(r) > 28 else ""
        kfm_status = r[29].strip() if len(r) > 29 else ""
        kfm_note = r[30].strip() if len(r) > 30 else ""

        # Xác định Bên chịu lỗi (Responsible Party)
        if store_fault.lower() == "siêu thị" or "st" in error_type.lower():
            responsible_party = "Siêu thị"
        elif dc_fault.lower() == "dc" or "dc" in error_type.lower():
            responsible_party = "DC"
        else:
            responsible_party = "Chưa xác định"

        # Phân luồng theo Step
        # Step 5: KFM đã xác nhận Done
        if kfm_status.lower() == "done" or process_status.lower() == "hoàn thành":
            step = 5
        # Step 4: DC đã xác nhận (Đồng ý / Kiểm tra lại) nhưng KFM chưa Done
        elif dc_confirm != "":
            step = 4
        # Step 3: Đã có chứng từ xử lý (PT trả về, PT bổ sung, camera)
        elif pt_return_st or pt_return_dc or pt_extra or camera_link:
            step = 3
        # Step 2: Đã phân loại nguyên nhân lỗi nhưng chưa có hướng xử lý
        elif error_type != "":
            step = 2
        # Step 1: Mới phát sinh chênh lệch giao nhận
        else:
            step = 1

        records.append({
            "record_id": record_unique_id,
            "transfer_date": transfer_date,
            "source_id": source_id,
            "source_name": source_name,
            "receiver_name": receiver_name,
            "id_st": id_st,
            "basket_code": basket_code,
            "basket_name": basket_name,
            "qty_sent": qty_sent,
            "qty_received": qty_received,
            "diff_qty": diff_qty,
            "pt_code": pt_code,
            "trip_code": trip_code,
            "basket_id": basket_id,
            "to_code": to_code,
            "return_st_qty": return_st_qty,
            "cxd_diff_qty": cxd_diff_qty,
            "pt_return_st": pt_return_st,
            "pt_return_dc": pt_return_dc,
            "pt_extra": pt_extra,
            "note1": note1,
            "error_type": error_type,
            "store_fault": store_fault,
            "dc_fault": dc_fault,
            "process_status": process_status,
            "camera_link": camera_link,
            "timeline": timeline,
            "dc_confirm": dc_confirm,
            "dc_note": dc_note,
            "kfm_status": kfm_status,
            "kfm_note": kfm_note,
            "step": step,
            "responsible_party": responsible_party
        })

    return records


def sync_sheet_to_database() -> Dict[str, Any]:
    """Tải từ Google Sheets và đồng bộ toàn diện vào SQLite Database."""
    init_database()
    rows = fetch_sheet_raw_csv()
    records = parse_and_classify_records(rows)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    total_rows = len(records)
    new_rows = 0
    updated_rows = 0

    for rec in records:
        # Cập nhật danh sách Store nếu có tên
        if rec["id_st"] and rec["id_st"] != "Khác":
            cursor.execute("""
                INSERT OR IGNORE INTO stores (id_st, store_name)
                VALUES (?, ?)
            """, (rec["id_st"], rec["receiver_name"]))

        # Kiểm tra xem record đã tồn tại chưa
        cursor.execute("SELECT record_id FROM doi_soat_records WHERE record_id = ?", (rec["record_id"],))
        exists = cursor.fetchone()

        if exists:
            updated_rows += 1
            cursor.execute("""
                UPDATE doi_soat_records SET
                    transfer_date = ?, source_id = ?, source_name = ?, receiver_name = ?,
                    id_st = ?, basket_code = ?, basket_name = ?, qty_sent = ?,
                    qty_received = ?, diff_qty = ?, pt_code = ?, trip_code = ?,
                    basket_id = ?, to_code = ?, return_st_qty = ?, cxd_diff_qty = ?,
                    pt_return_st = ?, pt_return_dc = ?, pt_extra = ?, note1 = ?,
                    error_type = ?, store_fault = ?, dc_fault = ?, process_status = ?,
                    camera_link = ?, timeline = ?, dc_confirm = ?, dc_note = ?,
                    kfm_status = ?, kfm_note = ?, step = ?, responsible_party = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE record_id = ?
            """, (
                rec["transfer_date"], rec["source_id"], rec["source_name"], rec["receiver_name"],
                rec["id_st"], rec["basket_code"], rec["basket_name"], rec["qty_sent"],
                rec["qty_received"], rec["diff_qty"], rec["pt_code"], rec["trip_code"],
                rec["basket_id"], rec["to_code"], rec["return_st_qty"], rec["cxd_diff_qty"],
                rec["pt_return_st"], rec["pt_return_dc"], rec["pt_extra"], rec["note1"],
                rec["error_type"], rec["store_fault"], rec["dc_fault"], rec["process_status"],
                rec["camera_link"], rec["timeline"], rec["dc_confirm"], rec["dc_note"],
                rec["kfm_status"], rec["kfm_note"], rec["step"], rec["responsible_party"],
                rec["record_id"]
            ))
        else:
            new_rows += 1
            cursor.execute("""
                INSERT INTO doi_soat_records (
                    record_id, transfer_date, source_id, source_name, receiver_name,
                    id_st, basket_code, basket_name, qty_sent, qty_received, diff_qty,
                    pt_code, trip_code, basket_id, to_code, return_st_qty, cxd_diff_qty,
                    pt_return_st, pt_return_dc, pt_extra, note1, error_type, store_fault,
                    dc_fault, process_status, camera_link, timeline, dc_confirm, dc_note,
                    kfm_status, kfm_note, step, responsible_party
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec["record_id"], rec["transfer_date"], rec["source_id"], rec["source_name"], rec["receiver_name"],
                rec["id_st"], rec["basket_code"], rec["basket_name"], rec["qty_sent"], rec["qty_received"], rec["diff_qty"],
                rec["pt_code"], rec["trip_code"], rec["basket_id"], rec["to_code"], rec["return_st_qty"], rec["cxd_diff_qty"],
                rec["pt_return_st"], rec["pt_return_dc"], rec["pt_extra"], rec["note1"], rec["error_type"], rec["store_fault"],
                rec["dc_fault"], rec["process_status"], rec["camera_link"], rec["timeline"], rec["dc_confirm"], rec["dc_note"],
                rec["kfm_status"], rec["kfm_note"], rec["step"], rec["responsible_party"]
            ))

    # Ghi log sync
    cursor.execute("""
        INSERT INTO sync_logs (total_rows, new_rows, updated_rows, status, message)
        VALUES (?, ?, ?, 'SUCCESS', 'Đồng bộ từ Google Sheets hoàn tất thành công')
    """, (total_rows, new_rows, updated_rows))

    conn.commit()
    conn.close()

    # Tính toán lại Datapay
    recalculate_datapay(period="2026-09")

    return {
        "status": "success",
        "total_rows": total_rows,
        "new_rows": new_rows,
        "updated_rows": updated_rows
    }


def recalculate_datapay(period: str = "2026-09"):
    """
    Tính toán Datapay (bồi hoàn chênh lệch thùng rổ) cho kỳ đối soát.
    Gom nhóm theo ID Siêu thị và Mã rổ, tính thành tiền dựa trên đơn giá bồi hoàn.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Xóa dữ liệu kỳ cũ để cập nhật mới
    cursor.execute("DELETE FROM datapay_records WHERE period = ?", (period,))

    # Lấy bảng giá thùng rổ
    cursor.execute("SELECT basket_code, unit_price FROM basket_types")
    prices = {row["basket_code"]: row["unit_price"] for row in cursor.fetchall()}

    # Gom nhóm theo ST và Mã rổ đối với các bản ghi có lỗi thuộc Siêu Thị và có chênh lệch âm (thiếu rổ)
    query = """
        SELECT 
            id_st,
            basket_code,
            responsible_party,
            SUM(CASE WHEN diff_qty < 0 THEN ABS(diff_qty) ELSE 0 END) AS total_missing,
            SUM(return_st_qty) AS total_resolved,
            SUM(CASE WHEN cxd_diff_qty > 0 THEN cxd_diff_qty ELSE 0 END) AS total_cxd
        FROM doi_soat_records
        WHERE responsible_party = 'Siêu thị'
        GROUP BY id_st, basket_code
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    for r in rows:
        id_st = r["id_st"]
        b_code = r["basket_code"]
        missing = r["total_missing"] or 0
        resolved = r["total_resolved"] or 0
        cxd = r["total_cxd"] or 0

        # Số lượng thực tế còn nợ đền bù = Thiếu - Đã trả hoàn trả
        net_owe = max(0, missing - resolved)
        unit_price = prices.get(b_code, 100000.0)
        total_amount = net_owe * unit_price

        cursor.execute("""
            INSERT INTO datapay_records (
                id_st, period, basket_code, missing_qty, resolved_qty,
                net_owe_qty, unit_price, total_amount, responsible_party
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_st, period, b_code, missing, resolved, net_owe, unit_price, total_amount, "Siêu thị"))

    conn.commit()
    conn.close()
    return True


def get_pipeline_summary() -> Dict[str, Any]:
    """Thống kê tổng quan dữ liệu theo 5 Step phân luồng và Datapay."""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Thống kê theo Step
    cursor.execute("SELECT step, COUNT(*) as cnt FROM doi_soat_records GROUP BY step")
    step_counts = {row["step"]: row["cnt"] for row in cursor.fetchall()}

    # Thống kê theo Bên chịu lỗi
    cursor.execute("SELECT responsible_party, COUNT(*) as cnt FROM doi_soat_records GROUP BY responsible_party")
    party_counts = {row["responsible_party"]: row["cnt"] for row in cursor.fetchall()}

    # Tổng Datapay kỳ 2026-09
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT id_st) as total_stores_owe,
            SUM(net_owe_qty) as total_net_owe_baskets,
            SUM(total_amount) as total_datapay_amount
        FROM datapay_records
    """)
    datapay_stat = cursor.fetchone()

    conn.close()

    return {
        "steps": {
            "step1_new_diff": step_counts.get(1, 0),
            "step2_classified": step_counts.get(2, 0),
            "step3_in_progress": step_counts.get(3, 0),
            "step4_dc_confirmed": step_counts.get(4, 0),
            "step5_completed": step_counts.get(5, 0),
        },
        "responsible_parties": party_counts,
        "datapay": {
            "total_stores_owe": datapay_stat["total_stores_owe"] or 0,
            "total_net_owe_baskets": datapay_stat["total_net_owe_baskets"] or 0,
            "total_datapay_amount": datapay_stat["total_datapay_amount"] or 0.0,
        }
    }

if __name__ == "__main__":
    print("Khởi tạo CSDL & Đồng bộ Google Sheet...")
    res = sync_sheet_to_database()
    print("Kết quả sync:", res)
    summary = get_pipeline_summary()
    print("Thống kê Phân luồng & Datapay:", summary)
