import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("H:/My Drive/Lynguyen/groups.json", "r", encoding="utf-8") as f:
    groups = json.load(f)

print(f"Total groups: {len(groups)}")

# Filter DC groups
dc_groups = {}
for gid, g in groups.items():
    title = g.get("title", "").strip()
    cat = g.get("category", "")
    if cat == "dc" or title.upper().startswith("DC"):
        dc_groups[gid] = g

print(f"DC groups: {len(dc_groups)}")

# Test stores from our matched 37 stores:
test_stores = ['A101', 'A104', 'A105', 'A117', 'A120', 'A131', 'A135', 'A139', 'A141', 'A148', 'A156', 'A169', 'A200', 'A201', 'A207', 'A225', 'A242', 'ACU', 'AV4', 'BQI', 'JKD']

for st in test_stores:
    matched = []
    pattern = re.compile(rf"\b{re.escape(st)}\b", re.IGNORECASE)
    for gid, g in dc_groups.items():
        title = g.get("title", "")
        if pattern.search(title) or f"DC - {st}".lower() in title.lower() or f"DC-{st}".lower() in title.lower():
            matched.append((gid, title))
    print(f"Store '{st}' -> {matched}")
