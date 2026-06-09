# sql_agent.py
client = None

def generate_or_heal_sql(user_query: str, schema: str, error_context: str = "") -> str:
    global client
    if client is None:
        raise ValueError("Gemini Client has not been initialized.")
        
    system_prompt = (
        "You are an elite autonomous Data Analyst Agent specializing in SQLite syntax.\n"
        "Your sole task is to convert a user's natural language question into perfectly executable SQL code.\n\n"
        
        "CRITICAL DATABASE STIPULATIONS:\n"
        "1. SQLite text matching can be case-sensitive. To prevent 0-row returns, ALWAYS wrap text column searches in LOWER() functions.\n"
        "2. When looking for Bangalore or Banglore, use: LOWER(location) LIKE '%bengaluru%'\n"
        "3. The column 'monthly_salary' contains pure numeric integers/floats. Use it for mathematical criteria (> 30000).\n"
        "4. Always ensure you add 'WHERE monthly_salary IS NOT NULL' to prevent structural logic evaluation failures.\n\n"
        
        "MANDATORY EXECUTABLE TEMPLATE FOR BANGALORE HIGH SALARIES:\n"
        "SELECT * FROM jobs WHERE LOWER(location) LIKE '%bengaluru%' AND monthly_salary > 30000 AND monthly_salary IS NOT NULL;\n\n"
        
        "CRITICAL FORMATTING:\n"
        "Return ONLY the raw SQL query. Do not use markdown backticks, code block formatting (```sql), or conversational introduction sentences.\n\n"
        f"Database Metadata Schema Structure:\n{schema}\n"
        f"Execution History / Corrections needed:\n{error_context}"
    )
    
    # FIX: Completely removed 'temperature' to bypass strict Pydantic validation rules
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=user_query,
        config={
            'system_instruction': system_prompt
        }
    )
    
    clean_sql = response.text.strip()
    clean_sql = clean_sql.replace("```sql", "").replace("```", "").strip()
    clean_sql = clean_sql.strip('`').strip()
    return clean_sql