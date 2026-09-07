import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import starrocks_db

def inspect_tables():
    conn = starrocks_db.get_starrocks_connection()
    cur = conn.cursor()
    
    target_tables = [
        "krc_dashboard_telegram_groups",
        "krc_dashboard_messages",
        "krc_dashboard_slg_base_data",
        "krc_dashboard_discrepancies",
        "krc_datapay_records",
        "krc_datapay_summary"
    ]
    
    for t in target_tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            cur.execute(f"DESC `{t}`")
            cols = cur.fetchall()
            print("Columns:")
            for col in cols:
                print(f"  - {col[0]} ({col[1]})")
                
            cur.execute(f"SELECT COUNT(*) FROM `{t}`")
            cnt = cur.fetchone()[0]
            print(f"Total rows: {cnt}")
            
            if cnt > 0:
                cur.execute(f"SELECT * FROM `{t}` LIMIT 2")
                rows = cur.fetchall()
                print("Sample rows:")
                for r in rows:
                    print("   ", r)
        except Exception as e:
            print(f"Error inspecting {t}: {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_tables()
