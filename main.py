import os
from rag_pipeline import run_rag_pipeline
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Energy Market RAG API",
    description="A FastAPI backend for querying the Energy Market Knowledge Assistant.",
    version="1.0.0"
)

# Pydantic models for request and response validation
class QueryRequest(BaseModel):
    query: str

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the importance of energy trading?"
            }
        }

class QueryResponse(BaseModel):
    query: str
    answer: str

# Paths for vector db
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

@app.post("/api/v1/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Accepts a user query, processes it through the RAG pipeline, and returns the LLM's answer.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        # Check if Google API key is present
        if not os.environ.get("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="Server Configuration Error: GOOGLE_API_KEY environment variable is not set."
            )

        # Ensure vector DB exists (optional but good for basic validation)
        if not os.path.exists(DB_DIR):
            raise HTTPException(
                status_code=500,
                detail="Server Configuration Error: Vector database directory ('chroma_db') not found."
            )

        # Run the RAG pipeline
        answer = run_rag_pipeline(query=request.query, persist_dir=DB_DIR)
        
        return QueryResponse(query=request.query, answer=answer)
    
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to let FastAPI handle them correctly
        raise http_exc
    except Exception as e:
        # Catch-all for unexpected pipeline errors (e.g. LLM failure, vector DB reading error)
        print(f"Error during RAG pipeline execution: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request. Please try again later."
        )

@app.get("/")
async def root():
    return {"message": "Welcome to the Energy Market RAG API. Visit /docs for the API documentation."}
