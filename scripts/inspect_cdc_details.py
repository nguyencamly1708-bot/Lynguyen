import sys
import os
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import starrocks_db

def inspect_cdc_schemas():
    conn = starrocks_db.get_starrocks_connection()
    cur = conn.cursor()
    
    samples = [
        "__cdc_kfm_kf_inventories_kf_transfer_items___container_lines",
        "__cdc_kfm_kf_transfer_tickets_kf_transfer_tickets",
        "__cdc_kfm_kf_inventories_kf_trip_locations___tl_received_pts",
        "__cdc_kfm_kf_inventories_kf_hrw_quality_tickets"
    ]
    
    for t in samples:
        print(f"\n==================== {t} ====================")
        cur.execute(f"DESC `{t}`")
        cols = cur.fetchall()
        for col in cols[:12]:
            print(f"  {col[0]}: {col[1]}")
        if len(cols) > 12:
            print(f"  ... và {len(cols) - 12} cột khác")
            
    conn.close()

if __name__ == "__main__":
    inspect_cdc_schemas()
