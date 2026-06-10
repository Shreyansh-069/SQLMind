import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.express as px
from src.agents import initialize_agentic_chat
from src import core

st.set_page_config(page_title="JobSeek - Intelligent Market Analyst", layout="wide")
st.title("📊 JobSeek - Intelligent Market Analyst")

schema_blueprint = core.get_db_schema()

# --- Initialize Stateful Memory Containers ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # Stores UI rendering transcripts

if "agent_session" not in st.session_state:
    st.session_state["agent_session"] = None  # Holds active Gemini token memory

if "last_active_dataframe" not in st.session_state:
    st.session_state["last_active_dataframe"] = None

if "last_active_sql" not in st.session_state:
    st.session_state["last_active_sql"] = None

# --- Sidebar Configuration Layout ---
with st.sidebar:
    st.header("🔑 Authentication")
    user_api_key = st.text_input(
        "Enter your Gemini API Key:", type="password", placeholder="AIzaSy..."
    )
    
    if user_api_key and st.session_state["agent_session"] is None:
        core.configure_gemini_client(user_api_key)
        # Spin up the stateful system agent
        st.session_state["agent_session"] = initialize_agentic_chat(schema_blueprint)
        st.success("✅ Agent Session Online with Memory!")

    st.markdown("---")
    if st.button("🧹 Clear Chat History & Reset Memory"):
        st.session_state["chat_history"] = []
        st.session_state["agent_session"] = None
        st.session_state["last_active_dataframe"] = None
        st.session_state["last_active_sql"] = None
        st.rerun()

    st.markdown("---")
    with st.expander("View Active SQL Table Columns"):
        st.text(schema_blueprint)

# --- Render Existing Chat UI History Transcripts ---
for message in st.session_state["chat_history"]:
    # Select clean monochrome icons to override default red/yellow styling
    current_avatar = "👤" if message["role"] == "user" else "📊"
    with st.chat_message(message["role"], avatar=current_avatar):
        st.markdown(message["content"])

# --- Chat Input Pipeline Loop ---
if user_input := st.chat_input("Ask me anything (e.g., 'Show me 3 Python jobs in Bangalore', then follow up with 'Compare them')"):
    
    # 1. Show user message in UI with clean silhouette icon
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state["chat_history"].append({"role": "user", "content": user_input})

    # 2. Process Agent Execution Response with clean analytics icon
    with st.chat_message("assistant", avatar="📊"):
        if st.session_state["agent_session"] is None:
            st.error("Please insert a valid Gemini API Key in the sidebar layout to initialize the Conversational Agent.")
        else:
            # Wipe tracking states prior to invocation to check if agent chooses to fire database tool
            st.session_state["last_active_dataframe"] = None
            st.session_state["last_active_sql"] = None

            with st.spinner("Agent is reasoning and executing steps..."):
                try:
                    # Pass prompt into continuous memory pipeline stream
                    response = st.session_state["agent_session"].send_message(user_input)
                    st.markdown(response.text)
                    st.session_state["chat_history"].append({"role": "assistant", "content": response.text})
                except Exception as api_err:
                    st.error(f"Agent Loop Execution Interrupted: {api_err}")

    # 3. Dynamic Rendering Interceptor (Catches tool adjustments and draws visual grids below response text)
    if st.session_state["last_active_dataframe"] is not None:
        df = st.session_state["last_active_dataframe"]
        sql = st.session_state["last_active_sql"]
        
        with st.expander("📊 View Live Data Matrix & Analytical Chart Outputs", expanded=True):
            st.code(sql, language="sql")
            st.dataframe(df, use_container_width=True)
            
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            text_cols = df.select_dtypes(include=["object"]).columns.tolist()
            
            if len(df) > 0:
                x_ax = text_cols[0] if text_cols else df.columns[0]
                y_ax = numeric_cols[0] if numeric_cols else df.columns[-1]
                
                fig = px.bar(
                    df, x=x_ax, y=y_ax,
                    title=f"{y_ax.upper()} VISUAL ANALYSIS",
                    template="plotly_dark", color=y_ax,
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)