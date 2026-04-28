from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import rag_service
from app.core.config import settings
import os

router = APIRouter(prefix="/v1")

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not set.")

    if not os.path.exists(settings.DB_DIR) or not os.listdir(settings.DB_DIR):
        raise HTTPException(status_code=500, detail="Vector database not initialized.")

    try:
        answer = rag_service.run_pipeline(request.query)
        return QueryResponse(query=request.query, answer=answer)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred.")
