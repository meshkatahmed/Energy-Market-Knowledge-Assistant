import os
from abc import ABC, abstractmethod
from typing import List, Type
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    Docx2txtLoader,
    TextLoader,
)

class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        pass

class PDFLoaderStrategy(BaseLoader):
    def load(self, file_path: str) -> List[Document]:
        return PyPDFLoader(file_path).load()

class CSVLoaderStrategy(BaseLoader):
    def load(self, file_path: str) -> List[Document]:
        return CSVLoader(file_path).load()

class ExcelLoaderStrategy(BaseLoader):
    def load(self, file_path: str) -> List[Document]:
        return UnstructuredExcelLoader(file_path).load()

class DocxLoaderStrategy(BaseLoader):
    def load(self, file_path: str) -> List[Document]:
        return Docx2txtLoader(file_path).load()

class TXTLoaderStrategy(BaseLoader):
    def load(self, file_path: str) -> List[Document]:
        return TextLoader(file_path).load()

class DocumentLoaderService:
    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        self._strategies = {
            ".pdf": PDFLoaderStrategy(),
            ".csv": CSVLoaderStrategy(),
            ".xlsx": ExcelLoaderStrategy(),
            ".xls": ExcelLoaderStrategy(),
            ".docx": DocxLoaderStrategy(),
            ".txt": TXTLoaderStrategy(),
        }

    def load_directory(self) -> List[Document]:
        all_documents = []
        if not os.path.exists(self.directory_path):
            print(f"Error: Directory '{self.directory_path}' does not exist.")
            return []

        for filename in os.listdir(self.directory_path):
            file_path = os.path.join(self.directory_path, filename)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in self._strategies:
                try:
                    print(f"Loading: {filename}")
                    all_documents.extend(self._strategies[ext].load(file_path))
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
            else:
                print(f"Skipping unsupported file: {filename}")

        return all_documents
