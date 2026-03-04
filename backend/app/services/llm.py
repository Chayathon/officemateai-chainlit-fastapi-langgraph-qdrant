from langchain_openai import ChatOpenAI
from app.core.config import settings

class LLMService:
    """Service สำหรับจัดการการเชื่อมต่อกับ LLM (vLLM)"""
    
    _instance: ChatOpenAI = None
    
    @classmethod
    def get_llm(cls) -> ChatOpenAI:
        """Singleton Pattern สำหรับ LLM Instance"""
        if cls._instance is None:
            cls._instance = ChatOpenAI(
                base_url=settings.VLLM_BASE_URL,
                api_key=settings.VLLM_API_KEY,
                model=settings.VLLM_MODEL_NAME,
                temperature=0.7,
                streaming=True
            )
        return cls._instance

# Shortcut
def get_llm() -> ChatOpenAI:
    return LLMService.get_llm()