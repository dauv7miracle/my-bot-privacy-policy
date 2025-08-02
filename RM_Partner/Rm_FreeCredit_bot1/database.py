import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DATA_DIR = 'data'
DB_FILE = os.path.join(DATA_DIR, 'bot_data.db')

def get_db_connection():
    """Creates a database connection."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # User points table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_points (
                    user_id INTEGER PRIMARY KEY,
                    referral_links INTEGER NOT NULL DEFAULT 0,
                    manual_adds INTEGER NOT NULL DEFAULT 0,
                    total INTEGER NOT NULL DEFAULT 0
                )
            ''')

            # Processed users table (to prevent double-counting)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS processed_users (
                    user_id INTEGER PRIMARY KEY,
                    source TEXT NOT NULL,
                    inviter_id INTEGER,
                    timestamp INTEGER NOT NULL
                )
            ''')
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)