from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Avisando o Pydantic pra olhar pro meu arquivo .env e pegar as variáveis de lá
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Nome do projeto e em que pé ele tá (dev, prod, etc)
    APP_NAME: str = "Hub Inteligente de Recursos Educacionais"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Onde o banco de dados vai ficar salvo (SQLite pra não ter que configurar servidor agora)
    DATABASE_URL: str = "sqlite:///./hub_educacional.db"

    # Coisas da Groq (IA) - a KEY eu deixo vazia pra colocar só no .env por segurança
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-70b-8192"
    GROQ_MAX_TOKENS: int = 512
    GROQ_TEMPERATURE: float = 0.4

    # URLs que o front-end vai usar (React, Vue, etc) pra o navegador não bloquear
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Controle pra não vir dado demais de uma vez nas listas
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # Se eu esquecer de colocar a chave no .env, o código reclama logo aqui
    @field_validator("GROQ_API_KEY")
    @classmethod
    def groq_key_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("GROQ_API_KEY não pode ser vazia")
        return v.strip()

    # Garante que o nível do log tá escrito certo, senão o Python buga
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL inválido. Use: {allowed}")
        return upper


# Esse cache é pra não ficar lendo o arquivo .env toda hora que eu precisar de uma config
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Essa é a variável que eu vou importar nos outros arquivos pra usar tudo isso
settings: Settings = get_settings()