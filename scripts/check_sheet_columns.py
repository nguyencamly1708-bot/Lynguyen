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

header = rows[0]
for idx, col in enumerate(header):
    print(f"Col {idx} ({chr(65 + idx) if idx < 26 else chr(64 + idx // 26) + chr(65 + idx % 26)}): {col}")

# Also find row for VGP
print("\n--- SAMPLE ROWS FOR VGP ---")
for r in rows[1:100]:
    if len(r) > 0 and r[0].strip() == "VGP":
        for i in range(min(len(r), 45)):
            if r[i].strip():
                print(f"  Col {i} ({header[i]}): {r[i]}")
        break
