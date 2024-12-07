import os
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from adapters.sql_adapter import get_db

class Query(BaseModel):
    question: str

gemini_api_key = "AIzaSyAT6hxKoCixNv1wQqoAzxzp5VrXxPlciDA" #os.getenv("OPENAI_API_KEY")  # Make sure to set this environment variable

# get mysql db
db = get_db()

template = """Based on the cricket related table schema below, write a SQL query that would answer the user's question, if the question is not related to cricket and the provided schema, don't give a sql response:
{schema}

Question: {question}
provide only plain sql query in the response.
SQL Query:"""
prompt = ChatPromptTemplate.from_template(template)

def get_schema(_):
    schema = db.get_table_info()
    return schema

llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, top_p=0.85,
                             google_api_key=gemini_api_key)

sql_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)


template = """Based on the table schema below, question, sql query, and sql response, write a natural language response, don't expose table ids:
{schema}

Question: {question}
SQL Query: {query}
SQL Response: {response}"""
prompt_response = ChatPromptTemplate.from_template(template)

def run_query(query):
    print("query::", query)
    return db.run(query)

full_chain = (
    # RunnablePassthrough.assign(query=sql_chain).assign(
    #     schema=get_schema,
    #     response=lambda vars: run_query(vars["query"][7:len(vars["query"])-3]),
    # )
    RunnablePassthrough.assign(schema=get_schema)
    | prompt_response
    | llm
    | StrOutputParser()
)

template = """This is a chat bot that answers cricket related questions, write a natural language response for the user question:
Question: {question}"""
normal_response = ChatPromptTemplate.from_template(template)

normal_chain = (
    normal_response
    | llm
    | StrOutputParser()
)

def convert_to_sql(query: str):
    sql_query = sql_chain.invoke({"question": query})
    sql_query = sql_query[7:len(sql_query)-3]
    print(sql_query)
    # if sql_query[:3] == "sql":
    #     sql_query = sql_query[:3]
    v = run_query(sql_query)
    print(v)
    return sql_query

def convert_nl_resp(query: str):
    print("convert_nl_resp",query)
    sql_query = sql_chain.invoke({"question": query})
    print(sql_query)
    if len(sql_query) > 10:
        try:
            db_resp = run_query(sql_query[7:len(sql_query) - 3])
            nl_resp = full_chain.invoke({"question": query, "query": sql_query, "response": db_resp})
        except Exception:
            nl_resp = "I don't have the right information to fulfil your query."
    else:
        nl_resp = normal_chain.invoke({"question": query})

    return nl_resp