import sqlite3
from config import DB_PATH
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        event TEXT
    )
    """)

    if not c.execute("SELECT * FROM users WHERE username='admin'").fetchone():
        c.execute("INSERT INTO users VALUES (?, ?)",
                  ("admin", generate_password_hash("1234")))

    conn.commit()
    conn.close()


def log_event(event):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO logs(time, event) VALUES (?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event))
    conn.commit()
    conn.close()


def get_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    logs = c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return logs


def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return user
