import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "local_db")
DB_PATH = os.path.join(DB_DIR, "nexus.db")


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database, creating the directory if needed."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _migrate_tables(conn) -> None:
    """Add new columns to existing tables if they don't exist yet."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(contracts)")}
    if "cost" not in existing:
        conn.execute("ALTER TABLE contracts ADD COLUMN cost TEXT")
    if "projected_return" not in existing:
        conn.execute("ALTER TABLE contracts ADD COLUMN projected_return TEXT")
    conn.commit()


def create_tables() -> None:
    """Create the contracts and delivery_procedures tables if they don't exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_map_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                area TEXT NOT NULL,
                initiative TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '1.0.0',
                description TEXT NOT NULL,
                owner TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                contact_name TEXT,
                contact_email TEXT,
                sec_approval TEXT,
                docs_link TEXT,
                cost TEXT,
                projected_return TEXT,
                usage TEXT,
                limitations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS delivery_procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL UNIQUE,
                tool_name TEXT NOT NULL,
                steps TEXT NOT NULL,
                documentation_path TEXT,
                contact_info TEXT
            );
        """)
        conn.commit()
        _migrate_tables(conn)
    finally:
        conn.close()
