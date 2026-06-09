# app.py
import time
import agents
import core
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="SelectAI Analytics Engine", layout="wide")
st.title("📊 SelectAI - Executive Job Market Analytics")

schema_blueprint = core.get_db_schema()

# --- Sidebar Layout ---
with st.sidebar:
    st.header("🔑 Authentication")
    user_api_key = st.text_input(
        "Enter your Gemini API Key:", type="password", placeholder="AIzaSy..."
    )
    st.markdown("---")
    
    st.header("🔌 Presentation Controls")
    demo_mode = st.checkbox("Enable Offline Demo Mode", value=False, 
                            help="Bypasses external API networks completely using local matching rules.")
    
    st.markdown("---")
    st.header("💡 Explore Suggested Queries")
    st.markdown("Select or type one of these phrases:")
    st.code("Remote Python Developer roles with salary over 15 LPA")
    st.code("Top 5 highest paying companies in Bangalore")
    st.code("Count of job openings per experience level")
    st.code("Average salary LPA for Senior (6-10 yrs) positions")
    
    st.markdown("---")
    with st.expander("View Active SQL Table Columns"):
        st.text(schema_blueprint)

# --- Batched Input Form Layout ---
with st.form(key="agent_analytics_form"):
    selected_sample = st.selectbox(
        "Quick-Select a Sample Query:",
        ["", 
         "Remote Python Developer roles with salary over 15 LPA",
         "Top 5 highest paying companies in Bangalore",
         "Count of job openings per experience level",
         "Average salary LPA for Senior (6-10 yrs) positions"]
    )
    
    user_query = st.text_input(
        "Or type custom query here:",
        value=selected_sample if selected_sample else "",
        placeholder="e.g., Show me Remote jobs with salary over 20 LPA",
    )
    submit_button = st.form_submit_button(label="🚀 Run Agent Analysis")

# Execution block begins only when the user deliberately submits the form
if submit_button and user_query:
    
    max_retries = 3
    success = False
    final_df = None
    executed_sql = ""
    insights = ""
    error_context = ""

    st.markdown("---")
    st.subheader("🤖 AGENT LIFECYCLE CHOREOGRAPHY :")

    # PATH A: OFFLINE DEMO MODE RUNPATH
    if demo_mode:
        st.success("⚡ **Offline Demo Mode Active:** Bypassed external API networks completely.")
        mock_sql, mock_insights = core.get_mock_query_mapping(user_query)
        
        if mock_sql:
            executed_sql = mock_sql
            insights = mock_insights
            db_status, final_df = core.run_sql_query(executed_sql)
            if db_status == "SUCCESS" and not final_df.empty:
                success = True
        else:
            st.warning("⚠️ This custom phrase is not pre-mapped in Offline Mode. Uncheck 'Enable Offline Demo Mode' to run live AI queries.")

    # PATH B: LIVE GEMINI EXECUTION RUNPATH
    else:
        if not user_api_key:
            st.error("Please provide an operational Gemini API key in the sidebar layout to run live mode.")
        else:
            # Initialize global Gemini configurations
            core.configure_gemini_client(user_api_key)
            
            with st.status("Spinning up Agent Pipeline...", expanded=True) as status:
                for attempt in range(1, max_retries + 1):
                    status.update(label=f"⏳ Executing Multi-Agent Loop {attempt}/{max_retries}...")
                    
                    with st.spinner("SQL Agent is writing query structure..."):
                        try:
                            executed_sql = agents.generate_or_heal_sql(
                                user_query, schema_blueprint, error_context
                            )
                            st.write(f"🧠 **SQL Agent (Attempt {attempt}):** Compiled targeted query logic.")
                        except Exception as err:
                            st.write(f"❌ **API Connection Error:** {err}")
                            status.update(label="Pipeline terminated.", state="error")
                            break
                    
                    with st.spinner("Querying analytics database engine..."):
                        db_status, result = core.run_sql_query(executed_sql)
                    
                    if db_status == "SUCCESS":
                        if result.empty:
                            st.write("ℹ️ **Database Engine:** Query ran successfully, but returned 0 records.")
                            final_df = result
                            success = True
                            break
                        else:
                            st.write(f"✅ **Database Engine:** Retrieved {len(result)} matching listings.")
                            final_df = result
                            success = True
                            break
                    else:
                        st.write(f"❌ **Database Engine Error:** Invalid Syntax.")
                        error_context = f"The expression '{executed_sql}' crashed. Technical reason: {result}"
                        time.sleep(1)

                if success and final_df is not None:
                    status.update(label="✨ Operational Metrics Extracted!", state="complete", expanded=False)

    # --- RENDERING ENGINE LAYER ---
    if success and final_df is not None and not final_df.empty:
        st.markdown("---")
        
        # Dynamic Metric Scorecards
        st.subheader("📊 EXECUTIVE SNAPSHOT METRICS :")
        m1, m2, m3 = st.columns(3)
        m1.metric("Postings Found", f"{len(final_df)} vacancies")
        
        if "salary_lpa" in final_df.columns and not final_df["salary_lpa"].isnull().all():
            m2.metric("Peak Compensation", f"₹{final_df['salary_lpa'].max():.1f} LPA")
            m3.metric("Average Market Pay", f"₹{final_df['salary_lpa'].mean():.1f} LPA")
        elif "max_salary" in final_df.columns:
            m2.metric("Peak Compensation", f"₹{final_df['max_salary'].max():.1f} LPA")
            m3.metric("Average Market Pay", f"₹{final_df['max_salary'].mean():.1f} LPA")
        elif "avg_salary_lpa" in final_df.columns:
            m2.metric("Overall Average Pay", f"₹{final_df['avg_salary_lpa'].mean():.1f} LPA")
        else:
            m2.metric("Peak Compensation", "N/A")
            m3.metric("Average Market Pay", "N/A")
            
        st.markdown("---")
        
        # Showcase the Business Summary Insights
        st.subheader("💡 EXECUTIVE SUMMARY INSIGHTS :")
        if not insights and not demo_mode:
            with st.spinner("Interpreter Agent is evaluating matrix for insights..."):
                try:
                    insights = agents.summarize_data_insights(
                        user_query, executed_sql, final_df
                    )
                except Exception as insight_err:
                    insights = f"Data table populated successfully! Summary rendering skipped: {insight_err}"
        st.info(insights)
        
        st.markdown("---")
        st.subheader("📋 LOGICAL SQL PATH UTILIZED :")
        st.code(executed_sql, language="sql")
        
        st.markdown("---")
        st.subheader("🗄️ PARSED RESULTS MATRIX :")
        st.dataframe(final_df, use_container_width=True)
        
        st.markdown("---")
        numeric_cols = final_df.select_dtypes(include=["number"]).columns.tolist()
        text_cols = final_df.select_dtypes(include=["object"]).columns.tolist()
        
        # High contrast dark-mode charts
        if len(final_df) > 0:
            st.subheader("📈 GRAPHICAL ANALYSIS :")
            
            x_ax = text_cols[0] if text_cols else final_df.columns[0]
            y_ax = numeric_cols[0] if numeric_cols else final_df.columns[-1]
            
            fig = px.bar(
                final_df,
                x=x_ax,
                y=y_ax,
                title=f"{y_ax.upper()} ANALYSIS BY {x_ax.upper()}",
                template="plotly_dark",
                color=y_ax,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
            
    elif final_df is not None and final_df.empty:
        st.markdown("---")
        st.subheader("📋 GENERATED SQL QUERY:")
        st.code(executed_sql, language="sql")
        st.warning("0 rows returned. The query format is syntactically sound, but no specific rows inside your dataset match these constraints.")