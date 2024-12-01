from fastapi import FastAPI
from routes.llm_routes import router

# Initialize the FastAPI app
app = FastAPI()

# Include the query controller routes
app.include_router(router)