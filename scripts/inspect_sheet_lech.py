import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import httpx, csv, io

url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"
res = httpx.get(url, timeout=30.0, follow_redirects=True)
content = res.content.decode("utf-8-sig", errors="ignore")
rows = list(csv.reader(io.StringIO(content)))

header = rows[0]
print(f"Total rows: {len(rows)}")

print("\n--- COLUMNS RELATING TO LECH / NHAN / XU LY ---")
for i, h in enumerate(header):
    if any(k in h.lower() for k in ['lệch', 'lech', 'chenh', 'chênh', 'tồn', 'nhận', 'trạng', 'xử lý', 'classify']):
        print(f"Col {i} ({chr(65 + i) if i < 26 else chr(64 + i // 26) + chr(65 + i % 26)}): {h}")


# Check conditions: AQ = Chờ ST phản hồi, AR = Đang xử lý
matching_rows = []
for idx, r in enumerate(rows[1:], start=2):
    if len(r) > 43:
        aq = r[42].strip().lower()
        ar = r[43].strip().lower()
        if "chờ st phản hồi" in aq and "đang xử lý" in ar:
            matching_rows.append((idx, r))

print(f"Matching rows (AQ='chờ st phản hồi' & AR='đang xử lý'): {len(matching_rows)}")

# Let's inspect SL chuyển (Col 11) vs SL nhận (Col 12) vs SL nhận HT (Col 13)
diff_count = 0
same_count = 0
st_set = set()
for idx, r in matching_rows:
    id_st = r[0].strip()
    st_set.add(id_st)
    sl_chuyen = r[11].strip()
    sl_nhan = r[12].strip()
    sl_nhan_ht = r[13].strip() if len(r) > 13 else ""
    if sl_chuyen != sl_nhan:
        diff_count += 1
    else:
        same_count += 1

print(f"Unique STs in matching rows: {len(st_set)}")
print(f"sl_chuyen != sl_nhan: {diff_count} rows")
print(f"sl_chuyen == sl_nhan: {same_count} rows")

print("\n--- ROWS WHERE SL_CHUYEN == SL_NHAN ---")
for idx, r in matching_rows:
    if r[11].strip() == r[12].strip():
        print(f"Row {idx} | ST: {r[0]} | SP: {r[9][:30]} | Chuyển: {r[11]} | Nhận: {r[12]} | Nhận HT: {r[13]} | TT: {r[20]}")


# Print first 10 rows showing id_st, ten_hang, sl_chuyen, sl_nhan, sl_nhan_ht, trang_thai
print("\n--- SAMPLE MATCHING ROWS ---")
for idx, r in matching_rows[:15]:
    print(f"Row {idx} | ST: {r[0]} | SP: {r[9][:30]} | Chuyển: {r[11]} | Nhận: {r[12]} | Nhận HT: {r[13]} | TT: {r[20]}")
