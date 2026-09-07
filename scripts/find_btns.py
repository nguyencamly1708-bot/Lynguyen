import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
with open("h:/My Drive/Lynguyen/static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "btnSyncAutoSheet" in l or "btnSyncStBroadcast" in l or "sync_and_broadcast_st" in l:
        print(f"Line {i+1}: {l.strip()}")
