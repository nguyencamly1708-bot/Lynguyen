import csv
import io
import sys
import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"

response = httpx.get(url, follow_redirects=True, timeout=15.0)
content = response.content.decode("utf-8-sig", errors="ignore")
rows = list(csv.reader(io.StringIO(content)))

header = rows[0]
classify_idx = 42 # Cột AQ là chỉ số 42

print(f"Tiêu đề cột AQ: '{header[classify_idx]}'")

unique_classify = set()
matched_rows = []

targets = [
    "chờ st phản hồi",
    "chờ dc nhận hàng",
    "hàng còn tại stote - sẽ chuyển theo chuyến gần nhất",
    "hàng còn tại store - sẽ chuyển theo chuyến gần nhất"
]

for idx, r in enumerate(rows[1:], start=2):
    if len(r) > classify_idx:
        val = r[classify_idx].strip()
        unique_classify.add(val)
        val_lower = val.lower()
        if any(t in val_lower for t in targets):
            matched_rows.append((idx, r))

print("\n--- Tất cả các giá trị Classify (Cột AQ) có trong Sheet ---")
for v in sorted(unique_classify):
    print(f" -> '{v}'")

print(f"\nTổng số dòng khớp điều kiện lọc: {len(matched_rows)}")
print("\nMẫu 3 dòng đầu tiên khớp:")
for r_num, r in matched_rows[:3]:
    id_st = r[0] if len(r) > 0 else ""
    ma_phieu = r[17] if len(r) > 17 else ""
    ten_hang = r[9] if len(r) > 9 else ""
    classify = r[42] if len(r) > 42 else ""
    print(f"Dòng {r_num}: ID ST={id_st} | Mã Phiếu={ma_phieu} | Tên Hàng={ten_hang} | Classify={classify}")
