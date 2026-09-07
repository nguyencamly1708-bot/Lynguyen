import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import starrocks_db

def inspect_db():
    conn = starrocks_db.get_starrocks_connection()
    with conn.cursor() as cur:
        cur.execute("SHOW GRANTS")
        grants = cur.fetchall()
        print("--- GRANTS ---")
        for g in grants:
            print(g[0])

        cur.execute("SHOW TABLES")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\n--- TABLES ({len(tables)}) ---")
        for t in tables:
            print(t)
            
    conn.close()

if __name__ == "__main__":
    inspect_db()
