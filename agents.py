# agents.py
import google.generativeai as genai
import pandas as pd

def generate_or_heal_sql(
    user_query: str, schema: str, error_context: str = ""
) -> str:
    """Translates natural language into SQLite code using Gemini's GenerativeModel structure."""
    system_prompt = (
        "You are an expert autonomous Data Analyst Agent specializing in SQLite.\n"
        "Convert the user's question into perfectly valid SQL code targeting the 'jobs' table.\n\n"
        "CRITICAL METRIC CONVERSION RULES:\n"
        "1. Compensation is stored as an annual float in Lakhs in the 'salary_lpa' column.\n"
        "   - If the user asks for thousands or raw numbers (e.g., 'more than 30,000', '> 50000', 'above 30k'), you MUST convert it to Lakhs Per Annum.\n"
        "   - Examples: 'salary > 30000' translates to -> salary_lpa > 0.3\n"
        "   - Examples: 'salary > 50000' translates to -> salary_lpa > 0.5\n"
        "   - Examples: '15 LPA' or '15 Lakhs' translates to -> salary_lpa > 15.0\n"
        "2. Geolocation filters run against the 'city' column. Treat 'Bangalore' and 'Bengaluru' as 'Bangalore'. Always use: LOWER(city) LIKE '%bangalore%'\n"
        "3. Filter programming stack keywords safely: LOWER(skills_required) LIKE '%python%'\n\n"
        "OUTPUT FORMATTING:\n"
        "Return ONLY the raw SQL query string. Never wrap it in markdown block characters (```sql) or add explanations."
    )

    user_context = f"Schema Blueprint:\n{schema}\n\nQuery History/Corrections:\n{error_context}\n\nUser Question: {user_query}"

    # Target gemini-1.5-flash for maximum generation speed and stability
    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite",
        system_instruction=system_prompt,
        generation_config={"temperature": 0.0}  # Strictly deterministic code generation
    )

    response = model.generate_content(user_context)
    
    clean_sql = (
        response.text.strip()
        .replace("```sql", "")
        .replace("```", "")
        .strip("`")
        .strip()
    )
    return clean_sql

def summarize_data_insights(
    user_query: str, executed_sql: str, data_df: pd.DataFrame
) -> str:
    """Generates concise executive analytics insights using the Gemini pipeline."""
    system_prompt = (
        "You are a professional business intelligence executive.\n"
        "Review the query and results summary to provide a clear, high-level 2-bullet point overview of findings."
    )

    context = f"Question: {user_query}\nSQL: {executed_sql}\nData Snippet:\n{data_df.head(5).to_string()}"

    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite",
        system_instruction=system_prompt,
        generation_config={"temperature": 0.3}
    )

    response = model.generate_content(context)
    return response.text.strip()