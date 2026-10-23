import sqlite3
from contextlib import contextmanager
from app.core.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    """Retorna una conexión activa a SQLite con row_factory habilitado y modo WAL."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

@contextmanager
def get_db_cursor():
    """Context manager para ejecutar transacciones SQL de forma segura."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
