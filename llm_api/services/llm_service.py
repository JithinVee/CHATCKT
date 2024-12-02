import os
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from adapters.sql_adapter import get_db

class Query(BaseModel):
    question: str

openai_api_key = os.getenv("OPENAI_API_KEY")  # Make sure to set this environment variable

# get mysql db
db = get_db()

template = """Based on the cricket table schema below, write a SQL query that would answer the user's question, if the question is a general greetings, for eg: 'hi', 'hello', 'how are you', 'good morning', don't give a sql response :
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


template = """Based on the cricket table schema below, question, sql query, and sql response, write a natural language response, dont expose table id details:
{schema}

Question: {question}
SQL Query: {query}
SQL Response: {response}"""
prompt_response = ChatPromptTemplate.from_template(template)

def run_query(query):
    print("query::", query)
    return db.run(query)

full_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt_response
    | llm
    | StrOutputParser()
)

template = """This is a chat bot that answers cricket related questions, write a natural language response for the user question:
Question: {question}
Response:"""
normal_response = ChatPromptTemplate.from_template(template)

normal_chain = (
    normal_response
    | llm
    | StrOutputParser()
)

def convert_to_sql(query: str):
    sql_query = sql_chain.invoke({"question": query})
    return sql_query

def convert_nl_resp(query: str):
    print("convert_nl_resp:",query)
    sql_query = sql_chain.invoke({"question": query})
    print(sql_query)
    if 'select' in sql_query.lower():
        try:
            db_resp = run_query(sql_query)
            nl_resp = full_chain.invoke({"question": query, "query": sql_query, "response": db_resp})
        except Exception:
            nl_resp = "I don't have the right information to fulfil your query."
    else:
        nl_resp = normal_chain.invoke({"question": query})

    return nl_resp