import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "career.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            age INTEGER,
            education TEXT,
            interests TEXT,
            skills TEXT,
            goal TEXT
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Database hazır:", DB_PATH)

# 👇 BU SATIR KRİTİK
if __name__ == "__main__":
    setup()
