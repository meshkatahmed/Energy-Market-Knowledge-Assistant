from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's natural language question.")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key drivers of electricity spot price volatility?"
            }
        }

class QueryResponse(BaseModel):
    query: str
    answer: str
    # Future: could add metadata like source documents or time taken
