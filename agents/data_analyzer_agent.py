# agents/data_analyzer_agent.py
# This worker agent is an expert in data analysis using SQL.

import pandas as pd
import duckdb
from openai import OpenAI

def run(df: pd.DataFrame, question: str, llm_client: OpenAI) -> any:
    """
    Entry point for the DataAnalysisAgent.
    It converts a natural language question into a SQL query and executes it.
    """
    print("DataAnalysisAgent: Running...")
    
    if df.empty or not question:
        return "Dataframe is empty or no question was provided."

    # Connect to an in-memory database and register the DataFrame
    con = duckdb.connect(database=':memory:')
    con.register("data_table", df)
    schema = con.execute("PRAGMA table_info('data_table');").fetchdf().to_string()

    # Create a precise prompt for the expert SQL agent
    sql_generation_prompt = f"""
You are an expert DuckDB SQL writer. Your ONLY job is to convert the user's question into a valid DuckDB SQL query.
The data is in a table named `data_table`. The schema is:
{schema}

Rules:
1.  Respond with ONLY the SQL query. Do not add any explanation or other text.
2.  Use double quotes for column names with special characters (e.g., "Worldwide gross").
3.  To use monetary strings (e.g., '$2,123,456') in calculations, first clean them by removing '$' and ',' and then cast to a numeric type.
"""
    
    response = llm_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sql_generation_prompt},
            {"role": "user", "content": question}
        ]
    )
    sql_query = response.choices[0].message.content.strip()
    print(f"DataAnalysisAgent: Generated SQL -> {sql_query}")

    try:
        result = con.execute(sql_query).fetchone()
        return result[0] if result else None
    finally:
        con.close()
