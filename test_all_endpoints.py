import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
import json


BASE_URL = "http://localhost:5000"

print("🔍 ĐANG KIỂM TRA TẤT CẢ CÁC ENDPOINT CỦA WEB DASHBOARD...\n")

endpoints = [
    ("/", "Trang chủ Index HTML"),
    ("/api/status", "Trạng thái Hệ thống & Bot"),
    ("/api/groups", "Danh sách Nhóm Telegram"),
    ("/api/history", "Lịch sử Gửi tin"),
    ("/api/mentions", "Lịch sử Phản hồi / Tag"),
]

with httpx.Client(timeout=10.0) as client:
    for ep, description in endpoints:
        url = f"{BASE_URL}{ep}"
        try:
            res = client.get(url)
            if res.status_code == 200:
                print(f"✅ {description} ({ep}): HTTP 200 OK")
                if "json" in res.headers.get("content-type", ""):
                    data = res.json()
                    print(f"   📊 Dữ liệu mẫu: {list(data.keys()) if isinstance(data, dict) else f'{len(data)} mục'}")
            else:
                print(f"❌ {description} ({ep}): Lỗi HTTP {res.status_code}")
        except Exception as e:
            print(f"❌ {description} ({ep}): Không thể kết nối - {e}")

print("\n🔍 KIỂM TRA HÀM PARSE DỮ LIỆU SHEET TRONG SERVER.PY...")
try:
    from server import fetch_and_parse_sheet
    grouped_st = fetch_and_parse_sheet()
    print(f"✅ Quét và lọc dữ liệu từ Google Sheet THÀNH CÔNG! Tìm thấy {len(grouped_st)} ID ST có phiếu cần phát:")
    for st_id, items in list(grouped_st.items())[:5]:
        print(f"   • ID ST: {st_id} - Có {len(items)} dòng phiếu đối soát")
except Exception as e:
    print(f"❌ Lỗi hàm fetch_and_parse_sheet: {e}")

