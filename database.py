import sqlite3
import threading
from contextlib import contextmanager

# Database configuration
DB_PATH = "data/asset_tags.db"

# Thread-local storage for database connections
_local = threading.local()

def get_connection():
    """Get a thread-local database connection"""
    if not hasattr(_local, 'connection'):
        _local.connection = sqlite3.connect(DB_PATH)
        _local.connection.row_factory = sqlite3.Row
    return _local.connection

@contextmanager
def get_db():
    """Context manager for database operations"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

# reminder: this is idempotent because of "if not exists" and "or ignore"
def init_database():
    """Initialize the database with our counter table"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_value INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Insert initial row if it doesn't exist
        conn.execute("""
            INSERT OR IGNORE INTO counters (id, current_value) 
            VALUES (1, 0)
        """)

def get_next_number():
    """Get the next number in the sequence"""
    with get_db() as conn:
        # Get current value and increment in a single transaction
        cursor = conn.execute("""
            UPDATE counters 
            SET current_value = current_value + 1 
            WHERE id = 1
            RETURNING current_value
        """)
        return cursor.fetchone()[0]