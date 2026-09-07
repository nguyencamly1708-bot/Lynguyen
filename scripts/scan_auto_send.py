import re

with open("h:/My Drive/Lynguyen/server.py", "r", encoding="utf-8") as f:
    content = f.read()

print("--- SEARCH FOR AUTOMATED / BACKGROUND SENDING ---")
matches = re.findall(r'(async def \w+|def \w+|setInterval|create_task|schedule|cron|sleep)', content, re.IGNORECASE)
for m in set(matches):
    print("Found keyword:", m)

lines = content.splitlines()
for idx, l in enumerate(lines):
    if any(k in l.lower() for k in ["create_task", "interval", "loop", "cron", "timer", "send_and_broadcast", "auto"]):
        if not any(ign in l for ign in ["auto_approve", "auto_accept", "autocomplete"]):
            print(f"Line {idx+1}: {l.strip()}")
