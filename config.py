import sqlite3
import pandas as pd
from google import genai

DB_NAME = "Chinook.db"

def get_gemini_client(api_key: str):
    """Dynamically initializes the Gemini Client with the user-provided API key."""
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def run_sql_query(query: str):
    """Executes a query against the backend system database.
    Returns: Tuple (status, pandas_dataframe_or_error_string)
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return "SUCCESS", df
    except Exception as e:
        return "ERROR", str(e)