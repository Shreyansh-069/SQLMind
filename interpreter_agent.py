# interpreter_agent.py
import pandas as pd

client = None

def summarize_data_insights(user_query: str, executed_sql: str, data_df: pd.DataFrame) -> str:
    global client
    if client is None:
        raise ValueError("Gemini Client has not been initialized in interpreter_agent.")

    summary_prompt = (
        "You are a professional business intelligence consultant.\n"
        "Review the target user query, the SQL logic path utilized, and the raw dataset matrix returned from the database infrastructure.\n"
        "Answer the user's question directly with a brief, friendly, clear summary analysis of the records."
    )
    
    user_context = (
        f"User Original Question: {user_query}\n"
        f"Executed SQL Path: {executed_sql}\n"
        f"Data Matrix Returned:\n{data_df.to_string()}"
    )
    
    # FIX: Completely removed 'temperature' to bypass strict Pydantic validation rules
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=user_context,
        config={
            'system_instruction': summary_prompt
        }
    )
    
    return response.text