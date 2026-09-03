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

classify_idx = 42 # AQ
header = rows[0]

targets = [
    "chờ st phản hồi",
    "chờ dc nhận hàng",
    "hàng còn tại stote - sẽ chuyển theo chuyến gần nhất",
    "hàng còn tại store - sẽ chuyển theo chuyến gần nhất"
]

grouped = {}

for r in rows[1:]:
    if len(r) > classify_idx:
        classify_val = r[classify_idx].strip()
        val_lower = classify_val.lower()
        if any(t in val_lower for t in targets):
            id_st = r[0].strip() if len(r) > 0 else "Khác"
            ma_phieu = r[17].strip() if len(r) > 17 else "" # Cột R
            chi_nhanh = r[3].strip() if len(r) > 3 else "" # Cột D
            ten_hang = r[9].strip() if len(r) > 9 else "" # Cột J
            sl = r[11].strip() if len(r) > 11 else "1" # Cột L

            if id_st not in grouped:
                grouped[id_st] = {
                    "chi_nhanh": chi_nhanh,
                    "phieu_set": set(),
                    "total_items": 0,
                    "items": []
                }
            if ma_phieu:
                grouped[id_st]["phieu_set"].add(f"{ma_phieu} ({classify_val})")
            grouped[id_st]["total_items"] += 1
            grouped[id_st]["items"].append({
                "ma_phieu": ma_phieu,
                "ten_hang": ten_hang,
                "sl": sl,
                "classify": classify_val
            })

text_msg = (
    "Ly gửi DS phiếu đối trả của tuần W29.2026 DC chưa nhận được hàng/chưa nhận được chứng từ.\n"
    "Hàng thực tế nếu đã bàn giao cho VT anh chị gửi giúp Ly ảnh chụp Phiếu chuyển/PGH.\n\n"
    "📌 **TỔNG HỢP THEO ID ST & MÃ PHIẾU:**\n"
)

for id_st, data in sorted(grouped.items()):
    phieu_list_str = ", ".join(sorted(data["phieu_set"]))
    text_msg += f"• **ST {id_st}** ({data['total_items']} dòng): {phieu_list_str}\n"

text_msg += (
    "\n*Sau hôm nay SCM sẽ trả tồn những phiếu này về ST.\n"
    "Cảm ơn các anh chị."
)

print(text_msg[:1500])
print(f"\n... (Đã tổng hợp {len(grouped)} ID ST, tổng chiều dài text: {len(text_msg)} ký tự)")
