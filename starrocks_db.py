import os
import json
import uuid
import datetime
import logging
from typing import Dict, Any, List
import pymysql
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

STARROCKS_HOST = os.getenv("STARROCKS_HOST", "103.147.122.103")
STARROCKS_PORT = int(os.getenv("STARROCKS_PORT", "9030"))
STARROCKS_USER = os.getenv("STARROCKS_USER", "kfm_scm_tho_nguyen")
STARROCKS_PASSWORD = os.getenv("STARROCKS_PASSWORD", "oh1dtJwR4ihLGrX4E7bs")
STARROCKS_DATABASE = os.getenv("STARROCKS_DATABASE", "kfm_scm")

def get_starrocks_connection():
    """Tạo kết nối tới cơ sở dữ liệu StarRocks."""
    return pymysql.connect(
        host=STARROCKS_HOST,
        port=STARROCKS_PORT,
        user=STARROCKS_USER,
        password=STARROCKS_PASSWORD,
        database=STARROCKS_DATABASE,
        charset="utf8mb4",
        connect_timeout=10,
        autocommit=True
    )

def test_starrocks_connection():
    """Kiểm tra trạng thái kết nối tới StarRocks."""
    try:
        conn = get_starrocks_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            ver = cur.fetchone()[0]
            
            cur.execute("SHOW TABLES")
            tables = [row[0] for row in cur.fetchall()]
            
        conn.close()
        return {
            "success": True,
            "version": ver,
            "tables": tables,
            "total_tables": len(tables)
        }
    except Exception as e:
        logger.error(f"Lỗi kết nối StarRocks: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def save_telegram_groups(groups_dict: Dict[str, Any]) -> int:
    """
    Lưu / đồng bộ danh sách nhóm Telegram vào bảng krc_dashboard_telegram_groups.
    Sử dụng INSERT INTO ... ON DUPLICATE KEY UPDATE / REPLACE.
    """
    if not groups_dict:
        return 0
    
    conn = get_starrocks_connection()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0
    
    # Batch insert into krc_dashboard_telegram_groups
    # Cols: group_id, group_name, group_type, discovered_at, updated_at
    sql = """
        INSERT INTO `krc_dashboard_telegram_groups` 
        (group_id, group_name, group_type, discovered_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    data = []
    for gid_str, info in groups_dict.items():
        try:
            gid = int(gid_str)
        except ValueError:
            continue
        gname = info.get("title", f"Group {gid_str}")
        gtype = info.get("category", "st")
        data.append((gid, gname, gtype, now_str, now_str))
        
    try:
        with conn.cursor() as cur:
            # StarRocks supports bulk insert
            batch_size = 200
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                cur.executemany(sql, batch)
                inserted += len(batch)
        conn.close()
    except Exception as e:
        logger.error(f"Lỗi lưu telegram_groups vào StarRocks: {e}")
        conn.close()
        raise e
        
    return inserted

def log_broadcast_message(
    telegram_msg_id: int,
    group_id: int,
    group_name: str,
    text: str,
    sender_name: str = "Ly Nguyen",
    sender_id: int = 0,
    image_path: str = "",
    message_type: str = "broadcast",
    group_type: str = "st"
) -> bool:
    """
    Ghi log tin nhắn phát tán vào bảng krc_dashboard_messages.
    """
    conn = get_starrocks_connection()
    msg_id_uuid = str(uuid.uuid4())
    now_dt = datetime.datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
        INSERT INTO `krc_dashboard_messages`
        (`id`, `telegram_msg_id`, `group_name`, `group_id`, `sender_name`, `sender_id`, 
         `text`, `image_path`, `message_type`, `timestamp`, `completed`, `feedback_text`, 
         `completed_by`, `group_type`, `created_at`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (
                msg_id_uuid,
                telegram_msg_id,
                group_name,
                group_id,
                sender_name,
                sender_id,
                text,
                image_path,
                message_type,
                now_str,
                1, # completed
                "", # feedback_text
                sender_name,
                group_type,
                now_dt
            ))
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Lỗi log tin nhắn vào StarRocks: {e}")
        conn.close()
        return False

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    res = test_starrocks_connection()
    if res["success"]:
        print(f"[SUCCESS] KET NOI STARROCKS THANH CONG!")
        print(f"Version: {res['version']}")
        print(f"Tables in '{STARROCKS_DATABASE}' ({res['total_tables']} tables):")
        for t in res["tables"][:15]:
            print(f"  - {t}")
    else:
        print(f"[FAIL] KET NOI THAT BAI: {res['error']}")
