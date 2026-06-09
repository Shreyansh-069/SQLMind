# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Import custom specialized layers
from schema_manager import get_db_schema
import sql_agent
import interpreter_agent
from config import run_sql_query, get_gemini_client

st.set_page_config(page_title="Enterprise SQL Agent Analytics", layout="wide")
st.title("📊 Enterprise Data Analyst Dashboard")

# Ingest metadata definitions using the Schema Manager component
try:
    schema_blueprint = get_db_schema()
except Exception:
    schema_blueprint = "Please ensure Chinook.db is present in the project folder."

# --- Sidebar Layout ---
with st.sidebar:
    st.header("🔑 Authentication")
    user_api_key = st.text_input(
        "Enter your Gemini API Key:", 
        type="password", 
        placeholder="AIzaSy..."
    )
    st.markdown("---")
    
    # PREMIUM MOVE: Quick Sample Prompts
    st.header("💡 Suggested Questions")
    st.markdown("Click one to copy-paste into the input box:")
    st.code("Jobs in banglore with salary more than 30000")
    st.code("Top 5 highest paying job titles in the dataset")
    st.code("Count of job openings per state")
    
    st.markdown("---")
    st.header("🗄️ System Metadata Map")
    with st.expander("View Database Schema Blueprint"):
        st.text(schema_blueprint)

# Question Input
user_query = st.text_input(
    "Ask your data a question in plain English:", 
    placeholder="e.g., Show me the top 5 highest paying job titles",
    disabled=not user_api_key
)

if user_query:
    if not user_api_key:
        st.error("Please enter your Gemini API key in the sidebar before proceeding.")
    else:
        # Initialize client and inject into background agents silently
        client_instance = get_gemini_client(user_api_key)
        sql_agent.client = client_instance
        interpreter_agent.client = client_instance
        
        # Internal Loop State Management
        max_retries = 3
        success = False
        final_df = None
        executed_sql = ""
        error_context_tracker = ""
        
        st.markdown("---")
        st.subheader("🤖 AGENT LIFECYCLE PROGRESS :")
        
        # Live-updating container for multi-agent choreography
        with st.status("Initializing Multi-Agent Data Pipeline...", expanded=True) as status:
            for attempt in range(1, max_retries + 1):
                status.update(label=f"⏳ Running Loop Attempt {attempt} of {max_retries}...")
                
                with st.spinner(f"SQL Agent is evaluating metadata structure and generating code..."):
                    try:
                        executed_sql = sql_agent.generate_or_heal_sql(user_query, schema_blueprint, error_context_tracker)
                        st.write(f"🧠 **SQL Agent (Attempt {attempt}):** Generated optimized SQL statement structure.")
                    except Exception as api_err:
                        st.write(f"❌ **API Error:** Core validation crashed: {str(api_err)}")
                        status.update(label="Pipeline terminated due to connection error.", state="error")
                        break
                
                with st.spinner(f"Database Engine is executing generated query against data infrastructure..."):
                    db_status, result = run_sql_query(executed_sql)
                
                if db_status == "SUCCESS":
                    if result.empty:
                        st.write(f"⚠️ **Execution Notice:** Query executed safely but returned 0 records.")
                        st.write(f"🩹 **Self-Healing Loop:** Retrying with fallback string matching configurations...")
                        error_context_tracker = (
                            f"\nYour previous query: '{executed_sql}' returned 0 rows.\n"
                            "CRITICAL CORRECTION: Use strictly LOWER(location) LIKE '%bengaluru%' for location filters.\n"
                            "Ensure case-insensitive operations using LOWER()."
                        )
                        final_df = result
                        time.sleep(1)
                    else:
                        st.write(f"✅ **Database Engine:** Data matrix successfully compiled ({len(result)} rows discovered).")
                        final_df = result
                        success = True
                        break
                else:
                    st.write(f"❌ **Database Error:** Execution crash detected.")
                    st.write(f"🩹 **Self-Healing Loop:** Feeding context back to SQL Agent to repair syntax...")
                    error_context_tracker = f"\nYour previous query: '{executed_sql}' failed with database engine error: '{result}'."
                    time.sleep(1)

            if success and final_df is not None and not final_df.empty:
                status.update(label="✨ Process Complete! All data metrics extracted successfully.", state="complete", expanded=False)
            else:
                status.update(label="🦖 Query execution finished completely but rows are 0.", state="complete", expanded=False)
                success = True

        # --- CLEAN RENDERING LAYER ---
        if success and final_df is not None and not final_df.empty:
            st.markdown("---")
            
            # PREMIUM MOVE: Dynamic KPI Cards
            st.subheader("📊 SNAPSHOT METRICS :")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric(label="Total Postings Found", value=f"{len(final_df)} roles")
            with m_col2:
                if 'monthly_salary' in final_df.columns and not final_df['monthly_salary'].isnull().all():
                    max_sal = int(final_df['monthly_salary'].max())
                    st.metric(label="Highest Monthly Salary Listed", value=f"₹{max_sal:,}")
                else:
                    st.metric(label="Highest Monthly Salary Listed", value="N/A (Text-based column)")
            with m_col3:
                if 'monthly_salary' in final_df.columns and not final_df['monthly_salary'].isnull().all():
                    avg_sal = int(final_df['monthly_salary'].mean())
                    st.metric(label="Average Monthly Salary", value=f"₹{avg_sal:,}")
                else:
                    st.metric(label="Average Monthly Salary", value="N/A")

            st.markdown("---")
            
            # PREMIUM MOVE: Showcase the Interpreter Agent
            st.subheader("💡 EXECUTIVE INSIGHTS ANALYSIS :")
            with st.spinner("Interpreter Agent is analyzing results matrix to draft summary..."):
                try:
                    ai_summary = interpreter_agent.summarize_data_insights(user_query, executed_sql, final_df)
                    st.info(ai_summary)
                except Exception as e:
                    st.warning(f"Interpreter Agent was unable to complete summary drafting: {e}")

            st.markdown("---")
            
            # 1. SQL QUERY SECTION
            st.subheader("📋 SQL QUERY PATH UTILIZED :")
            st.code(executed_sql, language="sql")
            
            st.markdown("---")
            
            # 2. TABLE SECTION
            st.subheader("🗄️ TABLE RELATED TO THE QUERY :")
            st.dataframe(final_df, use_container_width=True)
            
            st.markdown("---")
            
            # 3. CHART SECTION
            numeric_cols = final_df.select_dtypes(include=['number']).columns.tolist()
            text_cols = final_df.select_dtypes(include=['object']).columns.tolist()
            
            if numeric_cols and text_cols:
                st.subheader("📈 GRAPHICAL ANALYSIS :")
                x_ax = text_cols[0]
                # Target monthly_salary if present for chart mapping clarity
                y_ax = 'monthly_salary' if 'monthly_salary' in numeric_cols else numeric_cols[0]
                
                fig = px.bar(
                    final_df, 
                    x=x_ax, 
                    y=y_ax, 
                    title=f"{y_ax} BY {x_ax}".upper(),
                    template="plotly_dark",
                    color=y_ax,
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ The returned dataset structure does not contain a clear text/numeric pair to plot automatically.")
                
        elif final_df is not None and final_df.empty:
            st.markdown("---")
            st.subheader("📋 SQL QUERY GENERATED:")
            st.code(executed_sql, language="sql")
            st.warning("🦖 The query succeeded, but returned 0 rows. Your local SQLite text limits might be blocking exact keyword lookups.")