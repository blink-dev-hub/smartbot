import sqlite3
import logging

logger = logging.getLogger('SmartBot')

def setup_database(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            details TEXT
        )
    ''')
    conn.commit()
    return conn

def log_event(conn, event_type, details):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (event_type, details) VALUES (?, ?)", (event_type, details))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log event to database: {e}")

def get_recent_logs(conn, limit=100):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, event_type, details FROM events ORDER BY id DESC LIMIT ?", (limit,))
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Failed to fetch logs from database: {e}")
        return [] 