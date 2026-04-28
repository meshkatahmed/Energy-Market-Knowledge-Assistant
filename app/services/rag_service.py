from app.services.vector_store import vector_store_service
from app.services.llm_service import llm_service

class RAGService:
    def __init__(self):
        self.llm = llm_service

    def run_pipeline(self, query: str) -> str:
        # 1. Retrieve relevant context
        results = vector_store_service.similarity_search(query, k=3)
        context = "\n\n".join([doc.page_content for doc in results])
        
        # 2. Build the prompt
        prompt = f"""
        You are an Energy Market Knowledge Assistant. Use the provided context to answer the user's question accurately.
        If the answer is not in the context, politely state that you don't have that information.
        
        ---
        CONTEXT:
        {context}
        ---
        QUESTION: {query}
        ---
        ANSWER:
        """
        
        # 3. Generate the answer
        return self.llm.generate_response(prompt)

rag_service = RAGService()
