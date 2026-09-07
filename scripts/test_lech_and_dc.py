import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import httpx, csv, io, json, re

# Load groups
with open("groups.json", "r", encoding="utf-8") as f:
    groups = json.load(f)

url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"
res = httpx.get(url, timeout=30.0, follow_redirects=True)
content = res.content.decode("utf-8-sig", errors="ignore")
rows = list(csv.reader(io.StringIO(content)))

sys.path.insert(0, r"h:\My Drive\Lynguyen")
from server import find_dc_group_for_st

grouped_by_st = {}
skipped_no_lech = []

for r in rows[1:]:
    if len(r) > 43:
        aq_val = r[42].strip().lower()
        ar_val = r[43].strip().lower()

        if "chờ st phản hồi" in aq_val and "đang xử lý" in ar_val:
            id_st = r[0].strip() if len(r) > 0 else "Khác"
            sl_chuyen = r[11].strip() if len(r) > 11 else ""
            sl_nhan = r[12].strip() if len(r) > 12 else ""

            # Kiểm tra CÓ LỆCH:
            # Nếu sl_chuyen == sl_nhan và không rỗng và != "-1" -> Đã nhận đủ, KHÔNG LỆCH!
            if sl_chuyen == sl_nhan and sl_chuyen not in ["", "-1"]:
                skipped_no_lech.append((id_st, r[9], sl_chuyen, sl_nhan))
                continue

            if id_st not in grouped_by_st:
                grouped_by_st[id_st] = []

            grouped_by_st[id_st].append(r)

print(f"Tổng số ST có lệch: {len(grouped_by_st)}")
print(f"Các dòng bị bỏ qua do KHÔNG CÓ LỆCH (sl_chuyen == sl_nhan): {len(skipped_no_lech)}")
for x in skipped_no_lech:
    print(f"  - ST {x[0]}: {x[1]} (Chuyển {x[2]} == Nhận {x[3]})")

matched_dc = 0
unmatched_dc = []

for id_st in grouped_by_st.keys():
    gid, gtitle = find_dc_group_for_st(groups, id_st)
    if gid:
        matched_dc += 1
    else:
        unmatched_dc.append(id_st)

print(f"\nKhớp nhóm Telegram DC: {matched_dc}/{len(grouped_by_st)} ST")
print(f"Chưa tìm thấy nhóm DC: {len(unmatched_dc)} ST: {', '.join(unmatched_dc)}")
