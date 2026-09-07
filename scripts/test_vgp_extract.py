import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import httpx
import csv
import io

url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"
res = httpx.get(url, timeout=30.0, follow_redirects=True)
content = res.content.decode("utf-8-sig", errors="ignore")
rows = list(csv.reader(io.StringIO(content)))

print(f"Total rows in sheet: {len(rows)}")
vgp_rows = []
for r in rows[1:]:
    if len(r) > 43:
        aq_val = r[42].strip().lower()
        ar_val = r[43].strip().lower()
        if "chờ st phản hồi" in aq_val and "đang xử lý" in ar_val:
            id_st = r[0].strip()
            if id_st == "VGP":
                item = {
                    "id_st": r[0].strip(),
                    "ngay_chuyen": r[1].strip(),
                    "cn_chuyen": r[3].strip(),
                    "cn_nhan": r[4].strip(),
                    "ma_hang": r[8].strip(),
                    "ten_hang": r[9].strip(),
                    "dvt": r[10].strip(),
                    "sl_chuyen": r[11].strip(),
                    "sl_nhan": r[12].strip(),
                    "sl_nhan_ht": r[13].strip(),
                    "ma_chuyen_hang": r[17].strip(),
                    "trang_thai": r[20].strip(),
                    "tg_tao": r[41].strip(),
                }
                vgp_rows.append(item)

print(f"Found {len(vgp_rows)} items for VGP matching criteria:")
for idx, it in enumerate(vgp_rows[:5]):
    print(f"Row {idx+1}: {it}")
