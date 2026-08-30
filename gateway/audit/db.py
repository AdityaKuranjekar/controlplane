import sqlite3, json, time
from pathlib import Path

DB_PATH = Path("audit.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL,
            profile TEXT,
            prompt_redacted TEXT,
            action TEXT,
            reason TEXT,
            risk_vector TEXT,
            latency_ms TEXT,
            row_hash TEXT,
            prev_hash TEXT
        )
    """)
    conn.commit()
    conn.close()
