import urllib.request
import csv
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    raw = resp.read().decode("utf-8", errors="ignore")

rows = list(csv.reader(io.StringIO(raw)))
header = rows[0]

# filter rows
matched = []
for r in rows[1:]:
    if len(r) > 43:
        aq = r[42].strip().lower()
        ar = r[43].strip().lower()
        if "chờ st phản hồi" in aq and "đang xử lý" in ar:
            matched.append(r)

print(f"Matched rows: {len(matched)}")
# Check which columns in 0..41 have non-empty data across all matched rows
non_empty_cols = []
for c_idx in range(min(42, len(header))):
    values = [r[c_idx].strip() for r in matched if len(r) > c_idx and r[c_idx].strip()]
    if values:
        sample = values[0] if len(values) > 0 else ""
        non_empty_cols.append((c_idx, header[c_idx], len(values), sample))

print(f"Columns with non-empty data ({len(non_empty_cols)} columns):")
for col in non_empty_cols:
    print(f"  Col {col[0]} ({col[1]}): {col[2]}/{len(matched)} filled, sample='{col[3]}'")
