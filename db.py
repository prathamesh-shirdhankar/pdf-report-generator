"""
db.py
Small helper module: one function to get a connection, one to make sure
both tables exist. Nothing fancy — SQLite lives in a single file, report.db.
"""

import sqlite3

DB_PATH = "report.db"


def get_conn():
    """Open a connection to report.db. Every caller closes it when done."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read rows like dicts: row["amount"]
    return conn


def init_db():
    """Create the orders table and the reports table if they don't exist yet."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
