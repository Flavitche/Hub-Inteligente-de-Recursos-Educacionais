"""
Schemas Pydantic para o endpoint de geração inteligente via IA.
"""

from typing import List

from pydantic import BaseModel, Field

from app.schemas.resource import ResourceType


class AIGenerateRequest(BaseModel):
    """Payload de entrada para geração de descrição e tags por IA."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        examples=["Algoritmos e Estruturas de Dados em Python"],
    )
    type: ResourceType = Field(..., examples=["Video"])


class AIGenerateResponse(BaseModel):
    """Saída estruturada retornada pela IA."""

    description: str = Field(..., description="Descrição gerada automaticamente pelo LLM")
    tags: List[str] = Field(..., min_length=1, max_length=10, description="Tags relevantes geradas")


class AIUsageMetrics(BaseModel):
    """Métricas de uso dos tokens Groq (para observabilidade)."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    model: str
