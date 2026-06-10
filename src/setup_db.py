# src/setup_db.py
import sqlite3
import pandas as pd
import os

# 1. Define paths correctly relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
CSV_FILE = os.path.join(DATA_DIR, "india_job_market_2024_2026.csv")
DB_FILE = os.path.join(DATA_DIR, "analytics.db")

# 2. Ensure the 'data' directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"📁 Created missing directory: {DATA_DIR}")

print(f"⏳ Reading dataset from '{CSV_FILE}'...")

try:
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"The file {CSV_FILE} was not found.")

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
    print(f"📍 Database location: {DB_FILE}")

except FileNotFoundError as fnf_error:
    print(f"❌ Error: {fnf_error}")
except Exception as e:
    print(f"❌ Migration error encountered: {e}")