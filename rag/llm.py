"""
LLM models for PagePal application.
Provides access to language models.
"""

from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama

from config import config
from utils.logger import logger


@lru_cache(maxsize=2)  # Cache both streaming and non-streaming models
def get_llm_model(streaming: bool = False) -> ChatGoogleGenerativeAI:
    """
    Get the LLM model.
    Uses LRU cache to avoid creating multiple instances.

    Args:
        streaming: Whether to enable streaming

    Returns:
        ChatGoogleGenerativeAI: The LLM model
    """
    try:
        logger.info(
            f"Created LLM model: {config.LLM_MODEL} with {config.LLM_TO_USE} (streaming={streaming})"
        )

        match config.LLM_TO_USE:
            case "GEMINI":
                return ChatGoogleGenerativeAI(
                    model=config.LLM_MODEL,
                    google_api_key=config.GOOGLE_API_KEY,
                    temperature=0.7,
                    top_p=0.95,
                    convert_system_message_to_human=True,
                    streaming=streaming,  # Enable/disable streaming
                )
            case "GROQ":
                return ChatGroq(
                    model=config.LLM_MODEL,
                    temperature=0,
                    api_key=config.GROQ_API_KEY,
                    disable_streaming=not streaming,  # Use the streaming parameter
                    verbose=True,
                )
            case "DEEPSEEK":
                return ChatDeepSeek(
                    model=config.LLM_MODEL,
                    temperature=0,
                    api_key=config.DEEP_SEEK_API_KEY,
                    disable_streaming=not streaming,
                    verbose=True,
                )
            case "OLLAMA":
                return ChatOllama(
                    model=config.LLM_MODEL, temperature=0, stream=streaming
                )
            case _:
                raise ValueError(f"Unsupported LLM_TO_USE value: {config.LLM_TO_USE}")
    except Exception as e:
        logger.error(f"Failed to create LLM model: {e}")
        raise
