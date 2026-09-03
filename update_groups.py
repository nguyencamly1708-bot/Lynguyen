import json

active_groups = {
    "-5300068522": {
        "title": "DC - HLR (Thử)",
        "type": "group"
    }
}

with open("groups.json", "w", encoding="utf-8") as f:
    json.dump(active_groups, f, ensure_ascii=False, indent=2)

print("SUCCESS: Updated groups.json to active groups!")
