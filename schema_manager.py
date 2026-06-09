# schema_manager.py
import sqlite3
from config import DB_NAME

def get_db_schema() -> str:
    """Connects to the database to extract names and schema blueprints of tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema_text = ""
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
        # Normalizing to lowercase ensures smooth matching regardless of the download mirror source
        schema_text += f"Table: {table.lower()}\nColumns: {', '.join(columns).lower()}\n\n"
    conn.close()
    return schema_text