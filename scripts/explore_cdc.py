import sys
import os
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import starrocks_db


def explore_cdc_and_databases():
    conn = starrocks_db.get_starrocks_connection()
    cur = conn.cursor()
    
    print("=== 1. TẤT CẢ DATABASES TRÊN STARROCKS ===")
    cur.execute("SHOW DATABASES")
    dbs = [r[0] for r in cur.fetchall()]
    for db in dbs:
        print(f"  - {db}")
        
    print("\n=== 2. CÁC BẢNG CDC TRONG DATABASE 'kfm_scm' ===")
    cur.execute("SHOW TABLES LIKE '__cdc_%'")
    cdc_tables = [r[0] for r in cur.fetchall()]
    print(f"Tổng số bảng CDC trong kfm_scm: {len(cdc_tables)}")
    for t in cdc_tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM `{t}`")
            cnt = cur.fetchone()[0]
            print(f"  - {t}: {cnt} rows")
        except Exception as e:
            print(f"  - {t}: Error ({e})")
            
    # Check __cdc_schema_changes
    print("\n=== 3. NỘI DUNG BẢNG __cdc_schema_changes ===")
    try:
        cur.execute("DESC `__cdc_schema_changes`")
        print("Columns:")
        for col in cur.fetchall():
            print(f"  - {col[0]} ({col[1]})")
        cur.execute("SELECT * FROM `__cdc_schema_changes` LIMIT 10")
        rows = cur.fetchall()
        print(f"Sample rows ({len(rows)}):")
        for r in rows:
            print("   ", r)
    except Exception as e:
        print("Error inspecting __cdc_schema_changes:", e)
        
    # Also check if user has access to other databases and their CDC tables
    for db in dbs:
        if db in ["information_schema", "_statistics_", "kfm_scm"]:
            continue
        print(f"\n=== TABLES TRONG DB '{db}' ===")
        try:
            cur.execute(f"SHOW TABLES FROM `{db}`")
            tbls = [r[0] for r in cur.fetchall()]
            print(f"  Total tables: {len(tbls)}")
            for tbl in tbls[:15]:
                print(f"    - {tbl}")
        except Exception as e:
            print(f"  Không có quyền hoặc lỗi truy cập {db}: {e}")
            
    conn.close()

if __name__ == "__main__":
    explore_cdc_and_databases()
