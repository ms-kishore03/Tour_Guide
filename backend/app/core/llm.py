from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import get_settings


@lru_cache
def get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(groq_api_key=settings.groq_api_key, model_name="llama-3.1-8b-instant", temperature=0)
