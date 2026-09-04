import json
import re
import urllib.request
import csv
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 1. Load groups
with open("H:/My Drive/Lynguyen/groups.json", "r", encoding="utf-8") as f:
    groups = json.load(f)

# 2. Fetch sheet
url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    raw = resp.read().decode("utf-8", errors="ignore")

rows = list(csv.reader(io.StringIO(raw)))

# 3. Filter rows
matched_rows = []
for r in rows[1:]:
    if len(r) > 43:
        aq = r[42].strip().lower()
        ar = r[43].strip().lower()
        if "chờ st phản hồi" in aq and "đang xử lý" in ar:
            matched_rows.append(r)

st_list = sorted(list(set(r[0].strip() for r in matched_rows if r[0].strip())))
print(f"Total matched stores: {len(st_list)}")

def find_dc_group_for_st(groups: dict, id_st: str):
    id_st_clean = id_st.strip()
    pattern = re.compile(rf"\b{re.escape(id_st_clean)}\b", re.IGNORECASE)
    
    # Ưu tiên 1: Nhóm vừa có chữ 'DC' vừa chứa ID ST
    for gid, gdata in groups.items():
        title = gdata.get("title", "")
        cat = gdata.get("category", "")
        is_dc = (cat == "dc") or ("DC" in title.upper())
        if is_dc and pattern.search(title):
            return int(gid), title

    # Ưu tiên 2: Nhóm chứa 'DC - ID ST'
    for gid, gdata in groups.items():
        title = gdata.get("title", "")
        if f"dc - {id_st_clean}".lower() in title.lower() or f"{id_st_clean} - dc".lower() in title.lower():
            return int(gid), title

    # Ưu tiên 3: Nhóm bất kỳ chứa ID ST
    for gid, gdata in groups.items():
        title = gdata.get("title", "")
        if pattern.search(title):
            return int(gid), title

    return None, None

found_count = 0
not_found = []
for st in st_list:
    gid, title = find_dc_group_for_st(groups, st)
    if gid:
        found_count += 1
        print(f"✅ ST {st:5} -> Chat ID: {gid:15} | Group: {title}")
    else:
        not_found.append(st)
        print(f"❌ ST {st:5} -> KHÔNG TÌM THẤY NHÓM DC")

print(f"\nResult: {found_count}/{len(st_list)} stores matched DC groups!")
if not_found:
    print(f"Not found stores: {not_found}")
