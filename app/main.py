import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.chat import router as chat_router
from app.core.watcher import get_watcher_observer
from app.services.vector_store import vector_store_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.DB_DIR, exist_ok=True)
    
    # Initial build if needed
    if os.listdir(settings.DATA_DIR) and (not os.path.exists(settings.DB_DIR) or not os.listdir(settings.DB_DIR)):
        print(">> Performing initial vector store build...")
        vector_store_service.build_database(settings.DATA_DIR)

    observer = get_watcher_observer()
    observer.start()
    yield
    # Shutdown
    observer.stop()
    observer.join()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Energy Market RAG API is running.", "docs": "/docs"}
