import mariadb
import os
from dotenv import load_dotenv
load_dotenv()

try:
    print("🔄 Connecting...")
    conn = mariadb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        connect_timeout=5
    )
    print("✅ Connected!")

    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    print("📦 Tables:")
    for row in cur.fetchall():
        print(" -", row[0])

    conn.close()
except mariadb.Error as e:
    print("❌ Connection failed:")
    print(e)
