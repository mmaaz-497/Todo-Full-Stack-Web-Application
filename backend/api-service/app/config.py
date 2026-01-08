from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Database
    DATABASE_URL: str

    # OpenAI LLM
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2048
    
    # Better Auth
    AUTH_SECRET: str
    AUTH_ISSUER: str
    
    # Server
    MCP_SERVER_PORT: int = 3000
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    SYSTEM_ENABLED: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
