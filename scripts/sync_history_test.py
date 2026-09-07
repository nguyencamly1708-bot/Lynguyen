import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import uuid
import datetime
import starrocks_db

def sync_history():
    with open("h:/My Drive/Lynguyen/history.json", "r", encoding="utf-8") as f:
        history = json.load(f)

    print(f"Loaded {len(history)} history entries")
    data = []
    now_dt = datetime.datetime.now()
    
    for entry in history:
        ts = entry.get("timestamp", "")
        msg = entry.get("message", "")
        success_groups = entry.get("success_groups", [])
        if not success_groups and not msg:
            continue
            
        for gname in success_groups:
            uid = str(uuid.uuid4())
            data.append((
                uid,
                0,
                gname,
                0,
                "Ly Nguyen",
                0,
                msg[:5000],
                "",
                "broadcast",
                ts,
                1,
                "",
                "Ly Nguyen",
                "st",
                now_dt
            ))
            
    print(f"Prepared {len(data)} rows to insert")
    if not data:
        return
        
    conn = starrocks_db.get_starrocks_connection()
    cur = conn.cursor()
    
    sql = """
        INSERT INTO `krc_dashboard_messages`
        (`id`, `telegram_msg_id`, `group_name`, `group_id`, `sender_name`, `sender_id`,
         `text`, `image_path`, `message_type`, `timestamp`, `completed`, `feedback_text`,
         `completed_by`, `group_type`, `created_at`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        cur.executemany(sql, batch)
        print(f"Inserted {min(i + batch_size, len(data))}/{len(data)}...")
        
    cur.execute("SELECT COUNT(*) FROM `krc_dashboard_messages`")
    cnt = cur.fetchone()[0]
    print(f"Total rows in krc_dashboard_messages: {cnt}")
    conn.close()

if __name__ == "__main__":
    sync_history()
