import os
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from CHATCKT.llm_api.adapters.sql_adapter import get_db

class Query(BaseModel):
    question: str

openai_api_key = os.getenv("OPENAI_API_KEY")  # Make sure to set this environment variable

# get mysql db
db = get_db()

template = """Based on the table schema below, write a SQL query that would answer the user's question:
{schema}

Question: {question}
SQL Query:"""
prompt = ChatPromptTemplate.from_template(template)

def get_schema(_):
    schema = db.get_table_info()
    return schema

# llm = OpenAI(model="text-davinci-003", openai_api_key=openai_api_key)
llm = ChatOpenAI(openai_api_key=openai_api_key)

sql_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)


template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
{schema}

Question: {question}
SQL Query: {query}
SQL Response: {response}"""
prompt_response = ChatPromptTemplate.from_template(template)

def run_query(query):
    return db.run(query)

full_chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
        schema=get_schema,
        response=lambda vars: run_query(vars["query"]),
    )
    | prompt_response
    | llm
    | StrOutputParser()
)

def convert_to_sql(query: str):
    sql_query = sql_chain.invoke({"question": query})
    return sql_query

def convert_nl_resp(query: str):
    nl_resp = full_chain.invoke({"question": query})
    return nl_resp