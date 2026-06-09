# setup_db.py
import sqlite3
import pandas as pd
import os

def convert_csv_to_db():
    csv_filename = "job_market_india.csv"  # Points exactly to your uploaded file
    db_filename = "Chinook.db"            # Keep this name so config.py connects seamlessly
    
    if not os.path.exists(csv_filename):
        print(f"❌ Error: Cannot find '{csv_filename}' in this folder.")
        print("Please make sure it's placed in the exact same directory as this script!")
        return

    print(f"📖 Reading '{csv_filename}' into memory...")
    try:
        # Load your job dataset
        df = pd.read_csv(csv_filename)
        
        # Clean column headers: removes spaces and converts to lowercase for clean SQL usage
        # e.g., 'Job Title' becomes 'job_title', 'Monthly Salary' becomes 'monthly_salary'
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
        
        print(f"🗄️ Creating SQLite system file and injecting data rows...")
        conn = sqlite3.connect(db_filename)
        
        # Save the dataset inside the SQL environment under a table named 'jobs'
        df.to_sql("jobs", conn, if_exists="replace", index=False)
        conn.close()
        
        print(f"✅ Success! Your Indian Job Market dataset is completely converted.")
        print(f"📊 Active SQL Table Name: 'jobs'")
        print(f"📋 Accessible Columns for Gemini: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")

if __name__ == "__main__":
    convert_csv_to_db()