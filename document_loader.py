import os
import glob
from typing import List
from pathlib import Path
from langchain_core.documents import Document

# Document Loaders
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredExcelLoader,
)

class EnergyDocumentLoader:
    """
    A unified document loader for energy trading documents.
    Supports CSV (prices/trades), PDF (market reports), Excel (models/data), 
    Word (contracts/analysis), and plain text.
    """
    
    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        
    def _get_loader_for_file(self, file_path: str):
        """Returns the appropriate LangChain loader based on the file extension."""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return PyPDFLoader(file_path)
        elif ext == '.csv':
            return CSVLoader(file_path, encoding='utf-8')
        elif ext in ['.xls', '.xlsx']:
            return UnstructuredExcelLoader(file_path)
        elif ext == '.docx':
            return Docx2txtLoader(file_path)
        elif ext == '.txt':
            return TextLoader(file_path, encoding='utf-8')
        else:
            print(f"Unsupported file type: {ext} for file {file_path}")
            return None

    def load_single_document(self, file_path: str) -> List[Document]:
        """Loads a single document and returns a list of LangChain Document objects."""
        loader = self._get_loader_for_file(file_path)
        if loader:
            try:
                print(f"Loading {file_path}...")
                return loader.load()
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                return []
        return []

    def load_directory(self) -> List[Document]:
        """
        Scans the directory for all supported documents and loads them.
        Returns a flattened list of all loaded Document objects.
        """
        all_documents = []
        
        if not os.path.isdir(self.directory_path):
            raise AssertionError(f"Directory not found: {self.directory_path}")
            
        print(f"Scanning directory: {self.directory_path}")
        
        # Recursively find all files
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                docs = self.load_single_document(file_path)
                all_documents.extend(docs)
                
        print(f"Successfully loaded {len(all_documents)} total document segments/pages.")
        return all_documents


if __name__ == "__main__":
    # Example usage:
    # 1. Create a raw_data directory inside your project
    data_dir = os.path.join(os.path.dirname(__file__), "raw_data")
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"Please place your energy trading documents in: {data_dir}")
    print("Testing loader initialization...\n")
    
    loader = EnergyDocumentLoader(directory_path=data_dir)
    documents = loader.load_directory()
    
    if documents:
        # print(f"First document preview: {documents[0].page_content[:200000]}...")
        print(documents[30].page_content[:200000])
