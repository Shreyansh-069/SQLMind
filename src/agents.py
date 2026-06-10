# src/agents.py
import sqlite3
import pandas as pd
import google.generativeai as genai
import os
import streamlit as st

# FIXED PATH: Look inside the 'data' folder, one level up from 'src'
base_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(base_dir, "..", "data", "analytics.db")

def query_job_database(sql_query: str) -> str:
    """
    Executes a raw SQLite query against the 'jobs' database table.
    """
    print(f"DEBUG: Attempting to connect to DB at: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        if df.empty:
            return "Query executed successfully, but 0 matching records were found."
        
        st.session_state["last_active_dataframe"] = df
        st.session_state["last_active_sql"] = sql_query
        
        return df.to_string(index=False)
    except Exception as err:
        return f"Database Error: {str(err)}. Please correct your SQL syntax and try again."

def initialize_agentic_chat(schema_blueprint: str):
    """Initializes a stateful Gemini Chat Session armed with database tools and historical memory."""
    
    system_instruction = (
        "You are an expert Executive AI Data Agent specializing in the Indian Job Market.\n"
        "You have direct access to a local SQLite database table called 'jobs' via the 'query_job_database' tool.\n\n"
        "CORE CAPABILITIES:\n"
        "1. DATA RETRIEVAL: When asked about job counts, salaries, locations, or skills, translate the question into a valid SQLite query and invoke 'query_job_database'.\n"
        "2. FOLLOW-UPS: Use conversational memory to analyze previous results."
    )

    # Initialize model with the live executable tool
    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite",
        tools=[query_job_database],
        system_instruction=system_instruction,
        generation_config={"temperature": 0.2}
    )

    return model.start_chat(enable_automatic_function_calling=True)