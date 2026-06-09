# core.py
import sqlite3
import pandas as pd
import google.generativeai as genai

DB_PATH = "analytics.db"

def configure_gemini_client(api_key: str):
    """Configures the global Gemini API connection state safely."""
    genai.configure(api_key=api_key)

def get_db_schema() -> str:
    """Extracts column definitions and data structures to guide AI agents."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name='jobs';")
    schema_info = cursor.fetchall()
    conn.close()
    
    if schema_info:
        return f"Table Context Structure:\n{schema_info[0][1]}"
    return "Error: Database table 'jobs' does not exist."

def run_sql_query(sql_query: str):
    """Executes SQL statements safely and returns a status flag with a DataFrame."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return "SUCCESS", df
    except Exception as err:
        return "ERROR", str(err)

def get_mock_query_mapping(user_query: str) -> tuple:
    """Provides instant local fallback query matches to bypass API limits during testing."""
    q_low = user_query.lower().strip()
    
    mapping = {
        "remote python developer roles with salary over 15 lpa": (
            "SELECT * FROM jobs WHERE LOWER(work_mode) = 'remote' AND LOWER(job_title) LIKE '%python%' AND salary_lpa > 15;",
            "Analysis shows high-paying remote Python developer positions across the dataset. The majority of these listings are concentrated within MNCs and Indian Unicorn startups, offering top-tier compensation packages that leverage distributed infrastructure."
        ),
        "top 5 highest paying companies in bangalore": (
            "SELECT company, MAX(salary_lpa) AS max_salary, city FROM jobs WHERE LOWER(city) = 'bangalore' GROUP BY company ORDER BY max_salary DESC LIMIT 5;",
            "The data indicates that top product-based tech firms and enterprise services lead the compensation charts in Bangalore. Peak LPA packages focus heavily on roles requiring senior technical ownership and cloud execution skills."
        ),
        "count of job openings per experience level": (
            "SELECT experience_level, SUM(openings) AS total_openings FROM jobs GROUP BY experience_level ORDER BY total_openings DESC;",
            "Mid-level and Senior roles command the highest absolute volume of active vacancy listings. This shows a strong industry preference for independent contributors who can deliver immediate operational impact."
        ),
        "average salary lpa for senior (6-10 yrs) positions": (
            "SELECT experience_level, AVG(salary_lpa) AS avg_salary_lpa FROM jobs WHERE experience_level LIKE '%Senior%' GROUP BY experience_level;",
            "Senior talent metrics establish an impressive industry compensation baseline. Average payouts stay significantly elevated above junior categories, driven heavily by advanced system architecture and team management expectations."
        )
    }
    
    return mapping.get(q_low, (None, None))