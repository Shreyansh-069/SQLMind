# agents.py
import sqlite3
import pandas as pd
import google.generativeai as genai

DB_PATH = "analytics.db"

def query_job_database(sql_query: str) -> str:
    """
    Executes a raw SQLite query against the 'jobs' database table containing job market information.
    Use this tool whenever the user asks for metrics, lists, counts, or data lookups regarding jobs.
    Returns the results as a string representation of data rows.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        if df.empty:
            return "Query executed successfully, but 0 matching records were found."
        
        # Keep a global reference in Streamlit so the UI can capture and display the interactive table
        import streamlit as st
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
        "1. CHITCHAT/GENERAL CONVERSATION: If the user greets you, says thank you, or asks general questions, respond warmly and professionally without calling any tools.\n"
        "2. DATA RETRIEVAL: When asked about job counts, salaries, locations, or skills, translate the question into a valid SQLite query and invoke 'query_job_database'.\n"
        "3. FOLLOW-UPS & COMPARISONS: Maintain strict memory of the conversation. If a user asks to 'compare the first two' or asks follow-up details about a previous result, use your memory of the previous response to analyze and structure a comparative summary table or breakdown.\n\n"
        
        "CRITICAL SQL RULES:\n"
        "- The table name is 'jobs'.\n"
        "- Compensation is stored in Lakhs Per Annum in the 'salary_lpa' column (e.g., 15 LPA is written as 15.0). Always convert thousands/raw text numbers appropriately.\n"
        "- Treat 'Bangalore' and 'Bengaluru' interchangeably using: LOWER(city) LIKE '%bangalore%'\n"
        "- Filter skills using: LOWER(skills_required) LIKE '%python%'\n\n"
        
        "OUTPUT FORMATTING:\n"
        "Present your final answer to the user in clean, professional markdown with clear bullet points where helpful."
    )

    # Initialize model with the live executable tool attached
    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite",
        tools=[query_job_database],
        system_instruction=system_instruction,
        generation_config={"temperature": 0.2}
    )

    # start_chat returns a stateful session handler that automatically manages conversation memory tokens
    return model.start_chat(enable_automatic_function_calling=True)