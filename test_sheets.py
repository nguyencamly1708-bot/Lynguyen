import csv
import io
import sys
import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


url = "https://docs.google.com/spreadsheets/d/1qBEY7LP4FxCsrshblu0XQpBt2CCS5dX5pLiq9rAcXRk/export?format=csv&gid=788866159"

print("Đang tải dữ liệu từ Google Sheets...")
try:
    response = httpx.get(url, follow_redirects=True, timeout=15.0)
    print("HTTP Status Code:", response.status_code)
    if response.status_code == 200:
        content = response.content.decode("utf-8-sig", errors="ignore")
        reader = list(csv.reader(io.StringIO(content)))
        print(f"Tổng số dòng: {len(reader)}")
        if len(reader) > 0:
            header = reader[0]
            print(f"Số cột: {len(header)}")
            for idx, col in enumerate(header[:50]):
                col_letter = ""
                n = idx + 1
                while n > 0:
                    n, rem = divmod(n - 1, 26)
                    col_letter = chr(65 + rem) + col_letter
                print(f"Cột {col_letter} ({idx}): {col}")
    else:
        print("Không thể tải CSV, response:", response.text[:200])
except Exception as e:
    print("Lỗi:", e)
