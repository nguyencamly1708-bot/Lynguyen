import sys, json
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

h = json.load(open("history.json", encoding="utf-8"))
print(f"Total entries: {len(h)}")
for i, x in enumerate(h[-6:], start=len(h)-6):
    print(f"Index {i}: {x.get('timestamp')} | {x.get('type')} | {x.get('message')} | targets: {x.get('total_target')}")
