# setup_db.py
import sqlite3
import pandas as pd

CSV_FILE = "india_job_market_2024_2026.csv"
DB_FILE = "analytics.db"

print(f"⏳ Reading dataset from '{CSV_FILE}'...")
try:
    df = pd.read_csv(CSV_FILE)
    
    # Normalize headers to lowercase and clean up spaces to align with Agent rules
    df.columns = [col.strip().lower() for col in df.columns]
    
    print("🔄 Establishing connection to SQLite Database...")
    conn = sqlite3.connect(DB_FILE)
    
    # Store data inside the 'jobs' table
    df.to_sql("jobs", conn, if_exists="replace", index=False)
    
    # Verify migration schema
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name='jobs';")
    schema_info = cursor.fetchone()
    conn.close()
    
    print("✅ Database successfully initialized!")
    print(f"📦 Active Table Definition:\n{schema_info[1]}")

except FileNotFoundError:
    print(f"❌ Error: Could not find '{CSV_FILE}' in your active directory. Please verify file placement.")
except Exception as e:
    print(f"❌ Migration error encountered: {e}")