import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import starrocks_db

with open("h:/My Drive/Lynguyen/groups.json", "r", encoding="utf-8") as f:
    groups = json.load(f)

print(f"Loaded {len(groups)} groups from groups.json")
try:
    count = starrocks_db.save_telegram_groups(groups)
    print(f"Synced {count} groups to StarRocks table 'krc_dashboard_telegram_groups' successfully!")
except Exception as e:
    print(f"Sync error: {e}")
