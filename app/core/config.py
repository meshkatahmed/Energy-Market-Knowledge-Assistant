import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Energy Market RAG API"
    VERSION: str = "1.2.0"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "app", "data", "raw_data")
    
    VECTOR_STORE_TYPE: str = os.environ.get("VECTOR_STORE_TYPE", "chroma")
    
    @property
    def DB_DIR(self) -> str:
        # Dynamically creates a folder name like 'chroma_db' or 'milvus_db'
        folder_name = f"{self.VECTOR_STORE_TYPE.lower()}_db"
        return os.path.join(self.BASE_DIR, "app", "data", folder_name)
    
    # Model Providers
    LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "google")
    EMBEDDING_PROVIDER: str = os.environ.get("EMBEDDING_PROVIDER", "fastembed")
    
    GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY")
    
    # Model Configs
    CHAT_MODEL_NAME: str = "gemini-2.5-flash-lite"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    
    # Text splitter config
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150

settings = Settings()
