import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pymysql

HOST = "103.147.122.103"
PORT = 9030
USER = "kfm_scm_tho_nguyen"
PASSWORD = "oh1dtJwR4ihLGrX4E7bs"
DATABASE = "kfm_scm"

print(f"Connecting to StarRocks at {HOST}:{PORT}, db={DATABASE}, user={USER}...")
try:
    conn = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        connect_timeout=10,
        charset="utf8mb4"
    )
    print("SUCCESS: Connected to StarRocks!")
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        ver = cursor.fetchone()
        print(f"StarRocks Version: {ver}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Tables in '{DATABASE}' ({len(tables)} tables):")
        for t in tables[:15]:
            print(f"  - {t[0]}")
    conn.close()
except Exception as e:
    print(f"FAILED to connect: {e}")
