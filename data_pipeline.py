# data_pipeline.py
import os
import sqlite3
import pandas as pd


def run_ingestion_pipeline(
    source_csv="india_job_market_2024_2026.csv", target_db="analytics.db"
):
    print("🚀 Ingesting your new India Job Market dataset...")

    if not os.path.exists(source_csv):
        print(f"❌ Error: '{source_csv}' not found in the directory.")
        return

    # Load real dataset
    df = pd.read_csv(source_csv)
    print(f"📊 Discovered {len(df)} authentic job posting entries.")

    print("🧹 Cleaning and standardizing database column structures...")

    # 1. Standardize column names into snake_case
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # 2. Synchronize City naming variations (e.g., standardizing Bangalore/Bengaluru)
    if "city" in df.columns:
        df["city"] = df["city"].fillna("Unknown")
        df["city"] = df["city"].str.replace(
            "banglore", "Bangalore", case=False
        )
        df["city"] = df["city"].str.replace(
            "bengaluru", "Bangalore", case=False
        )

    # 3. Handle numeric column parsing
    if "salary_lpa" in df.columns:
        df["salary_lpa"] = pd.to_numeric(
            df["salary_lpa"], errors="coerce"
        ).fillna(0.0)

    # 4. Commit to the local SQLite engine
    conn = sqlite3.connect(target_db)
    df.to_sql("jobs", conn, if_exists="replace", index=False)

    # Quick verify
    check_df = pd.read_sql_query("SELECT * FROM jobs LIMIT 3;", conn)
    conn.close()

    print("\n🌟 VERIFIED DB SCHEMA SAMPLE:")
    print(check_df.to_string(index=False))
    print(
        f"\n✅ Pipeline Complete! Clean data matrix saved directly to '{target_db}'."
    )


if __name__ == "__main__":
    run_ingestion_pipeline()