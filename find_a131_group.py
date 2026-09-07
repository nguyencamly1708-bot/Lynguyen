import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r"h:\My Drive\Lynguyen\groups.json", "r", encoding="utf-8") as f:
    groups = json.load(f)

if isinstance(groups, dict):
    glist = [{"id": k, "name": v.get("title", ""), "category": v.get("category", "")} for k, v in groups.items()]
else:
    glist = groups

print(f"Total groups: {len(glist)}")
for g in glist:
    if "131" in g["name"]:
        print(f"ID: {g['id']} | Category: {g['category']} | Name: {g['name']}")
