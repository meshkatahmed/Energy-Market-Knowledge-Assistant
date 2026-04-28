from abc import ABC, abstractmethod
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings

class LLMInterface(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class GoogleGeminiService(LLMInterface):
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model=settings.CHAT_MODEL_NAME,
            temperature=0.1
        )

    def generate_response(self, prompt: str) -> str:
        response = self.model.invoke([HumanMessage(content=prompt)])
        return response.content

def get_llm_service() -> LLMInterface:
    if settings.LLM_PROVIDER.lower() == "google":
        return GoogleGeminiService()
    # Add OpenAI, Anthropic, etc. here
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")

llm_service = get_llm_service()
