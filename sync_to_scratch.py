import shutil, os

src_dir = r"h:\My Drive\Lynguyen"
dst_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"

files_to_sync = [
    "server.py",
    "userbot_sender.py",
    os.path.join("static", "index.html"),
    os.path.join("static", "app.js"),
    os.path.join("static", "style.css")
]

for rel_p in files_to_sync:
    src_p = os.path.join(src_dir, rel_p)
    dst_p = os.path.join(dst_dir, rel_p)
    if os.path.exists(src_p):
        shutil.copy2(src_p, dst_p)
        print(f"Synced: {rel_p}")
print("Sync finished.")
