
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    APP_NAME: str = "Hub Inteligente de Recursos Educacionais"
    ENVIRONMENT: str = "development"  
    LOG_LEVEL: str = "INFO"

    # Database 
    DATABASE_URL: str = "sqlite:///./hub_educacional.db"

    #  Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-70b-8192"
    GROQ_MAX_TOKENS: int = 512
    GROQ_TEMPERATURE: float = 0.4

    # CORS 
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Paginação
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    @field_validator("GROQ_API_KEY")
    @classmethod
    def groq_key_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("GROQ_API_KEY não pode ser vazia")
        return v.strip()

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL inválido. Use: {allowed}")
        return upper


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings: Settings = get_settings()
