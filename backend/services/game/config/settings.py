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
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 4000
    GROQ_TIMEOUT: int = 120
    
    # AI Generation Settings
    MAX_RETRY_ATTEMPTS: int = 3
    ENABLE_FALLBACK_GENERATOR: bool = True
    LOG_TOKEN_USAGE: bool = True
    
    # MongoDB (inherited from existing)
    MONGODB_URI: Optional[str] = None
    
    class Config:
        env_file = "backend/.env" 
        case_sensitive = True
        extra = "ignore"


# Singleton instance
settings = GameSettings()
