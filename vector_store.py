import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

from document_loader import EnergyDocumentLoader

def build_vector_database(raw_data_dir: str, persist_dir: str):
    # 1. Load the Documents
    print("Loading documents...")
    loader = EnergyDocumentLoader(directory_path=raw_data_dir)
    documents = loader.load_directory()
    
    if not documents:
        print("No documents found in raw_data. Please add some files and try again.")
        return None

    # 2. Split the Documents into Chunks
    print(f"Splitting {len(documents)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} searchable chunks.")

    # 3. Initialize your Embedding Model
    print("Initializing FastEmbed model (this may download the model on first run)...")
    embeddings = FastEmbedEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # 4. Create and Persist the Vector Store
    print("Building Vector Database (this may take a bit depending on document size)...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"Vector database successfully created at '{persist_dir}'!")
    return vector_store

def query_vector_database(query: str, persist_dir: str):
    print("Initializing embedding model for querying...")
    embeddings = FastEmbedEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    print(f"Loading database from '{persist_dir}'...")
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    
    print(f"Searching for: '{query}'")
    results = vector_store.similarity_search(query, k=3)
    
    print("\n--- Search Results ---\n")
    for i, match in enumerate(results, 1):
        print(f"Result {i} (Source: {match.metadata.get('source', 'Unknown')}):")
        print(f"{match.page_content}\n")
        print("-" * 40)
        
    return results

if __name__ == "__main__":
    DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
    DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Build the DB (Uncomment to rebuild when adding new docs)
    build_vector_database(DATA_DIR, DB_DIR)
    
    # 2. Example Query (Uncomment to test querying)
    query_vector_database("What is Media Soft?", DB_DIR)
    
    print(f"Vector store utilities are ready. Add some documents to '{DATA_DIR}'")
    print("Then open this script and uncomment 'build_vector_database' to build your DB.")
