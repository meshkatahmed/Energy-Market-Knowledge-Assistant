import os
from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from app.core.config import settings
from app.services.document_loader import DocumentLoaderService
from app.services.embedding_service import embedding_service

class VectorStoreInterface(ABC):
    @abstractmethod
    def build_database(self, raw_data_dir: str):
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        pass

class ChromaStore(VectorStoreInterface):
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.embeddings = embedding_service.get_embeddings()

    def build_database(self, raw_data_dir: str):
        print(">> [VectorStore] Loading documents...")
        loader = DocumentLoaderService(directory_path=raw_data_dir)
        documents = loader.load_directory()
        
        if not documents:
            print(">> [VectorStore] No documents found.")
            return None

        print(f">> [VectorStore] Splitting {len(documents)} documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE, 
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        print(">> [VectorStore] Indexing into ChromaDB...")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print(f">> [VectorStore] Database successfully created at '{self.persist_dir}'")
        return vector_store

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        vector_store = Chroma(
            persist_directory=self.persist_dir, 
            embedding_function=self.embeddings
        )
        return vector_store.similarity_search(query, k=k)

def get_vector_store() -> VectorStoreInterface:
    if settings.VECTOR_STORE_TYPE.lower() == "chroma":
        return ChromaStore(persist_dir=settings.DB_DIR)
    # Add MilvusStore implementation here in the future
    elif settings.VECTOR_STORE_TYPE.lower() == "milvus":
        return MilvusStore(...)
    else:
        raise ValueError(f"Unsupported vector store type: {settings.VECTOR_STORE_TYPE}")

vector_store_service = get_vector_store()
