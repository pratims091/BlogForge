"""
Configuration module for BlogForge application.
Loads environment variables and provides configuration settings.
"""

import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration settings for BlogForge application."""

    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    CRAWL4AI_API_TOKEN: str = os.getenv("CRAWL4AI_API_TOKEN", "")
    JINA_API_KEY: str = os.getenv("JINA_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEEP_SEEK_API_KEY: str = os.getenv("DEEP_SEEK_API_KEY", "")

    # search settings
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", 10))
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "GOOGLE")

    # Crawler settings
    CRAWLER_PROVIDER: str = os.getenv("CRAWLER_PROVIDER", "JINA")
    CRAWL4AI_HOST: str = os.getenv("CRAWL4AI_HOST", "http://crawl4ai:11235")
    CRAWL_TIMEOUT: int = int(os.getenv("CRAWL_TIMEOUT", "300"))  # 5 minutes

    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Vector store
    PERSIST_DIRECTORY: str = os.getenv("VECTOR_STORE_DIR", "data/chroma_db")

    # LLM settings
    LLM_TO_USE: str = os.getenv("LLM_TO_USE")
    LLM_MODEL: str = os.getenv("LLM_MODEL")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

    # Cache settings
    CACHE_EXPIRY_DAYS: int = int(os.getenv("CACHE_EXPIRY_DAYS", "30"))

    # Streaming settings
    STREAM_CHUNK_SIZE: int = int(
        os.getenv("STREAM_CHUNK_SIZE", "25")
    )  # Characters per chunk

    # Logging settings
    LOG_LEVEL_STR: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_LEVEL: int = getattr(logging, LOG_LEVEL_STR, logging.INFO)
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)

    URL_CRAWL_LIMIT: Optional[int] = os.getenv("URL_CRAWL_LIMIT", 100)

    @classmethod
    def validate(cls) -> Optional[str]:
        """
        Validate that all required configuration is present.

        Returns:
            Optional[str]: Error message if validation fails, None otherwise
        """
        required_vars = [
            "GOOGLE_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY",
        ]

        if cls.CRAWLER_PROVIDER == "JINA":
            required_vars.append("JINA_API_KEY")
        else:
            required_vars.append("CRAWL4AI_API_TOKEN")

        missing = [var for var in required_vars if not getattr(cls, var)]

        if missing:
            return f"Missing required environment variables: {', '.join(missing)}"

        return None

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith("__") and not callable(value)
        }


# Create a config instance for easy importing
config = Config()
