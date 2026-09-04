import urllib.request
import csv
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    raw = resp.read().decode("utf-8", errors="ignore")

rows = list(csv.reader(io.StringIO(raw)))
print(f"Total rows: {len(rows)}")
if rows:
    header = rows[0]
    print(f"Total columns: {len(header)}")
    for idx, col in enumerate(header):
        # convert index to excel col letters (0=A, 25=Z, 26=AA, 42=AQ, 43=AR)
        c = idx
        letters = ""
        while c >= 0:
            letters = chr(65 + (c % 26)) + letters
            c = c // 26 - 1
            if c < 0:
                break
        print(f"Col {idx} ({letters}): {col}")

    # Check sample unique values of AQ and AR
    # Find idx of AQ and AR
    # A=0, B=1, ... Z=25, AA=26 ... AQ=42, AR=43, AP=41
    print("\n--- Inspecting values in rows ---")
    aq_vals = set()
    ar_vals = set()
    matched_rows = []
    for r_idx, r in enumerate(rows[1:], start=2):
        if len(r) > 43:
            aq = r[42].strip()
            ar = r[43].strip()
            aq_vals.add(aq)
            ar_vals.add(ar)
            if "chờ st phản hồi" in aq.lower() and "đang xử lý" in ar.lower():
                matched_rows.append((r_idx, r[0].strip(), aq, ar, r[1:6]))

    print(f"Unique values in AQ (Classify): {aq_vals}")
    print(f"Unique values in AR (Xử lý): {ar_vals}")
    print(f"\nTotal matched rows (AQ='chờ ST phản hồi' & AR='đang xử lý'): {len(matched_rows)}")
    stores = set(m[1] for m in matched_rows)
    print(f"Unique stores in matched rows: {len(stores)} -> {sorted(list(stores))[:20]}")
    if matched_rows:
        print("\nSample 3 matched rows:")
        for m in matched_rows[:3]:
            print(f"Row {m[0]}: ID ST='{m[1]}', AQ='{m[2]}', AR='{m[3]}', Details={m[4]}")
