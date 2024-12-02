import traceback
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from services.llm_service import convert_to_sql, convert_nl_resp
# from services.g_service import convert_to_sql, convert_nl_resp

# Define the Pydantic model to handle input data
class Query(BaseModel):
    question: str

# Create a FastAPI Router for the query endpoint
router = APIRouter()

@router.get("/sql_query")
async def convert_sql_query(cmd: str):
    # Run the SQL chain to generate the SQL query from the input question
    try:
        print("query", cmd)
        sql_query = convert_to_sql(cmd)
        return JSONResponse(content={"status": False, "sql_query": sql_query})
    except Exception:
        traceback.print_exc()
        return JSONResponse(content={"status": False, "error_msg": "failed to get response"})


@router.post("/query")
async def convert_query(query: Query):
    # Run the FULL chain to generate the human-readable response from the input question
    try:
        print("query", query.question)
        result = convert_nl_resp(query.question)
        return JSONResponse(content={"status": True, "response": result})
    except Exception:
        traceback.print_exc()
        return JSONResponse(content={"status": False, "error_msg": "failed to get response"})