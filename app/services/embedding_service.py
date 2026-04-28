from abc import ABC, abstractmethod
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from app.core.config import settings

class EmbeddingInterface(ABC):
    @abstractmethod
    def get_embeddings(self):
        pass

class FastEmbedService(EmbeddingInterface):
    def __init__(self):
        self.embeddings = FastEmbedEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME
        )

    def get_embeddings(self):
        return self.embeddings

def get_embedding_service() -> EmbeddingInterface:
    if settings.EMBEDDING_PROVIDER.lower() == "fastembed":
        return FastEmbedService()
    # Add HuggingFace, OpenAI, etc. here
    else:
        raise ValueError(f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}")

embedding_service = get_embedding_service()
