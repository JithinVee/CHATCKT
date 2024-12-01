from fastapi import FastAPI
from routes.llm_routes import router
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the query controller routes
app.include_router(router)