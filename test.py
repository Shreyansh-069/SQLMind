# test_openai.py
from openai import OpenAI

# Paste your active OpenAI key here to check connection health
client = OpenAI(api_key="sk-abcdef1234567890abcdef1234567890abcdef12")

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Respond with 'Connection Confirmed' if you hear me."}],
        max_tokens=10
    )
    print("✅ OpenAI Status:", response.choices[0].message.content.strip())
except Exception as e:
    print("❌ Connection Failed. Check your balance or API key validation. Details:")
    print(e)