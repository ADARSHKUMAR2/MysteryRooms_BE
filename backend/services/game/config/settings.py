"""
Game Service Configuration Settings

Manages environment variables and application settings.
Single Responsibility: Configuration loading and validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class GameSettings(BaseSettings):
    """Game service configuration from environment variables"""

    # Groq API Configuration
    GROQ_API_KEY: str
    GROQ_MODELS: list[str] = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.6-27b",
        "openai/gpt-oss-20b",
    ]

    # --------------------------------
    # OPENAI CONFIGURATION
    # --------------------------------
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODELS: list[str] = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-3.5-turbo"
    ]

    # AI Generation Settings
    STORY_TEMPERATURE: float = 0.7
    PUZZLE_TEMPERATURE: float = 0.2
    GROQ_MAX_TOKENS: int = 6000
    GROQ_TIMEOUT: int = 120
    
    MAX_RETRY_ATTEMPTS: int = 3
    ENABLE_FALLBACK_GENERATOR: bool = True
    LOG_TOKEN_USAGE: bool = True

    # MongoDB
    MONGODB_URI: Optional[str] = None

    class Config:
        env_file = "backend/.env"
        case_sensitive = True
        extra = "ignore"


settings = GameSettings()
