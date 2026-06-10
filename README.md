# JobSeek-AI: Intelligent Market Analyst

JobSeek-AI is an agentic data analysis tool designed to provide deep insights into the Indian job market. By leveraging Google Gemini’s function-calling capabilities and a local SQLite engine, the system enables users to query complex job datasets using natural language.

**Access the live application here:** [https://jobseek-ai.streamlit.app](https://jobseek-ai.streamlit.app)

---

## 🏗️ Workflow & Architecture
The application follows a clean, modular architecture designed for scalability and maintainability.



1.  **Data Ingestion (`setup_db.py`):** Raw CSV data is ingested, cleaned, and standardized (e.g., city naming conventions, salary formatting) before being stored in a local SQLite database.
2.  **Database Layer (`core.py`):** Acts as the interface between the application logic and the SQLite database.
3.  **Agentic Logic (`agents.py`):** Uses Google Gemini 1.5-flash to interpret user requests. It identifies when to use tools (SQL queries) and maintains conversational memory to handle follow-up questions.
4.  **User Interface (`app.py`):** Built with Streamlit, it maintains session state for the chat history and dynamically renders data tables and charts using Plotly.

---

## 🛠️ Technology Stack
* **Frontend/UI:** [Streamlit](https://streamlit.io/)
* **AI/LLM:** [Google Gemini 1.5-Flash](https://deepmind.google/technologies/gemini/flash/)
* **Database:** [SQLite](https://www.sqlite.org/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/)
* **Visualization:** [Plotly](https://plotly.com/)

---

## 📂 Project Structure
```text
JobSeek-AI/
├── app.py              # Main Streamlit UI entry point
├── data/               # SQLite database and raw datasets
├── src/                # Core modular logic
│   ├── agents.py       # Agent definition, system instructions, and tool calling
│   ├── core.py         # Database schema utilities
│   └── setup_db.py     # Data ingestion and cleaning pipeline
├── .gitignore          # Excludes __pycache__ and system files
└── requirements.txt    # Project dependencies
```

## ⚙️ Setup Instructions
1. **Prerequisites**
Ensure you have Python 3.10+ installed.

2. **Installation**
  1. Clone the repository:
```text
git clone [https://github.com/yourusername/JobSeek-AI.git](https://github.com/yourusername/JobSeek-AI.git)
cd JobSeek-AI
```
  2. Install the required libraries:
```text
pip install -r requirements.txt
```
3. **Initialize the Database**  
Before running the app locally, ingest your dataset:
```text
python src/setup_db.py
```
4. **Run the Application**
Start the Streamlit interface:
```text
streamlit run app.py
```
## 💡 How to Use
1. API Setup: Enter your Google Gemini API Key in the sidebar.
2. Interaction: Once the "Agent Session" is online, start asking analytical questions:
                "What are the top 5 highest paying companies in Bangalore?"
                "Show me the distribution of job openings by experience level."
                "Compare the average salary of Senior vs Junior roles."
3. Analysis: The Agent will provide a textual summary, generate the corresponding SQL query, and render an interactive visualization automatically.  

## Built with ❤️ for data-driven job seekers.