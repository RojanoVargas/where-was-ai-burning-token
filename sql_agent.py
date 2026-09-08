from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from langchain_community.utilities import SQLDatabase
from langchain.tools import tool
import config
from model_config import chat_model_kwargs

load_dotenv()

sql_llm = ChatOpenAI(
    **chat_model_kwargs(),
    temperature=0,
)

db = SQLDatabase.from_uri(
    os.getenv("SUPABASE_DB_URL")
)

@tool
def sql_db_list_tables() -> str:
    """Input is an empty string, output is a comma-separated list of tables in the database."""
    return ", ".join(db.get_usable_table_names())

@tool
def sql_db_schema(table_names: str) -> str:
    """Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables.
    Be sure that the tables actually exist by calling sql_db_list_tables first!
    Example Input: table1, table2, table3"""
    valid_tables = set(db.get_usable_table_names())
    results = []
    for table in table_names.split(","):
        table = table.strip()
        if table not in valid_tables:
            results.append(f"Error: table_name '{table}' not found in database")
            continue
        try:
            schema = db.get_table_info(table_names=[table])
            sample = db.run(f'SELECT * FROM "{table}" LIMIT 3;')
            results.append(f"{schema}\n\nSample rows:\n{sample}")
        except Exception as e:
            results.append(f"Error fetching schema or sample rows for {table}: {e}")
    return "\n\n".join(results)

@tool
def sql_db_query(query: str) -> str:
    """Input to this tool is a detailed and correct SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    If you encounter an issue with Unknown column 'xxxx' in 'field list', use sql_db_schema to query the correct table fields."""
    try:
        return db.run(query)
    except Exception as e:
        return f"Error: {e}"

@tool
def sql_db_query_checker(query: str) -> str:
    """Use this tool to double check if your query is correct before executing it.
    Always use this tool before executing a query with sql_db_query!"""
    trigger_prompt = f"""{query}
Double check the SQL query above for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final SQL query only.

SQL Query: """
    response = sql_llm.invoke(trigger_prompt)
    return response.text.strip()

@tool
def get_current_episode_limit() -> str:
    """Return the current episode limit (no spoilers beyond this).
    Use this to decide if a question can be answered without spoiling.
    """
    return (
        f"Current user progress: only episodes with id <= {config.CURRENT_EPISODE_ID} are known. "
        f"Do NOT use or reveal information from episodes with id > {config.CURRENT_EPISODE_ID}."
    )

SQL_TOOLS = [
    sql_db_list_tables,
    sql_db_schema,
    sql_db_query,
    sql_db_query_checker,
    get_current_episode_limit,
]
