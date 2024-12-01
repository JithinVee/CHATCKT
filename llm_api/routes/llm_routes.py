from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from CHATCKT.llm_api.services.llm_service import convert_to_sql, convert_nl_resp

# Define the Pydantic model to handle input data
class Query(BaseModel):
    question: str

# Create a FastAPI Router for the query endpoint
router = APIRouter()

@router.get("/sql_query")
async def convert_query(query: Query):
    # Run the SQL chain to generate the SQL query from the input question
    sql_query = convert_to_sql(query.question)
    return JSONResponse(content={"sql_query": sql_query})

@router.post("/query")
async def convert_query(query: Query):
    # Run the FULL chain to generate the human-readable response from the input question
    result = convert_nl_resp(query.question)
    return JSONResponse(content={"response": result})