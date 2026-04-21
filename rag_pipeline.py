import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.prompts import PromptTemplate
from vector_store import build_vector_database

# We import ChatGoogleGenerativeAI to use Gemini models.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def run_rag_pipeline(query: str, persist_dir: str):
    # 1. Load the Vector Database
    print("--- Step 1: Loading Vector Database ---")
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    
    # 2. Retrieve related documents
    print(f"--- Step 2: Retrieving relevant documents for query: '{query}' ---")
    docs = vector_store.similarity_search(query, k=3)
    
    # Formulate context from retrieved documents
    context_texts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'Unknown')
        context_texts.append(f"--- Document {i} (Source: {source}) ---\n{doc.page_content}")
    context = "\n\n".join(context_texts)
    
    # 3. Generate a Prompt
    print("--- Step 3: Generating prompt ---")
    prompt_template = """You are a helpful and knowledgeable assistant for energy market topics.
Please answer the following user query based ONLY on the provided context documents.
If you cannot find the answer in the context, clearly stating that you do not know based on the provided documents; do not invent an answer.

{context}

User Query: {query}

Answer:"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "query"]
    )
    
    formatted_prompt = prompt.format(context=context, query=query)
    
    # Optional: print the prompt so you can see exactly what gets sent
    print("\n[Generated Prompt Preview]")
    # print(formatted_prompt[:300] + "\\... [truncated for brevity]")
    print(formatted_prompt)
    
    # 4. Pass the prompt to an LLM
    print("\n--- Step 4: Sending prompt to LLM ---")
    
    # WARNING: To use Gemini, you must set your Google API key.
    # You can set it in your environment: os.environ["GOOGLE_API_KEY"] = "AIza..."
    # If the token is not present, this initialization will raise an error.
    if not os.environ.get("GOOGLE_API_KEY"):
        print(">> NOTE: GOOGLE_API_KEY is not currently set in your environment variables.")
        print(">> The pipeline will fail on the next step without an API token.")
        print(">> Please set it via `os.environ[\"GOOGLE_API_KEY\"] = \"your_token\"`\n")

    chat_model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.1
    )
    
    print("Waiting for LLM response...")
    response = chat_model.invoke([HumanMessage(content=formatted_prompt)])
    answer = response.content
    
    print("\n" + "="*40)
    print("========== LLM ANSWER ==========")
    print("="*40)
    print(answer)
    print("================================\n")
    
    return answer

if __name__ == "__main__":
    load_dotenv()
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
    DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
    
    # build_vector_database(DATA_DIR,DB_DIR)
    
    test_query = "What are the importance of energy trading?"
    
    print("Executing pipeline for test query...")
    run_rag_pipeline(test_query, DB_DIR)
