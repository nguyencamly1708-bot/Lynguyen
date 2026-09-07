import re

with open("h:/My Drive/Lynguyen/static/app.js", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
for idx, l in enumerate(lines):
    if any(k in l.lower() for k in ["setinterval", "settimeout", "sync_and_broadcast", "broadcast", "auto"]):
        print(f"Line {idx+1}: {l.strip()[:100]}")
