import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import starrocks_db

def check_permissions():
    conn = starrocks_db.get_starrocks_connection()
    with conn.cursor() as cur:
        try:
            cur.execute("SHOW GRANTS FOR kfm_scm_tho_nguyen")
            print("--- GRANTS ---")
            for r in cur.fetchall():
                print(r)
        except Exception as e:
            print("Error SHOW GRANTS:", e)
            
        # Test creating a small staging or sync table to verify write permission
        test_table = "krc_bot_sync_test"
        try:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS `{test_table}` (
                    id INT,
                    msg VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=OLAP
                PRIMARY KEY(id)
                DISTRIBUTED BY HASH(id) BUCKETS 1
                PROPERTIES("replication_num" = "1");
            """)
            print("CREATE TABLE permission: OK")
            
            cur.execute(f"INSERT INTO `{test_table}` (id, msg) VALUES (1, 'test_conn')")
            print("INSERT permission: OK")
            
            cur.execute(f"SELECT * FROM `{test_table}`")
            print("SELECT rows:", cur.fetchall())
            
            cur.execute(f"DROP TABLE IF EXISTS `{test_table}`")
            print("DROP TABLE permission: OK")
        except Exception as e:
            print("Write permission test error:", e)
            
    conn.close()

if __name__ == "__main__":
    check_permissions()
