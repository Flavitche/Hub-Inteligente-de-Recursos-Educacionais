"""
Schemas Pydantic para o endpoint de geração inteligente via IA.
"""

from typing import List
from pydantic import BaseModel, Field
from app.schemas.resource import ResourceType


class AIGenerateRequest(BaseModel):
    """Payload de entrada para geração de descrição e tags por IA."""

    # O que o usuário precisa mandar. Botei limites pro título não vir vazio ou gigante.
    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        examples=["Algoritmos e Estruturas de Dados em Python"],
    )
    # Reutilizo o ResourceType (Video, PDF...) pra IA saber o contexto do que vai descrever
    type: ResourceType = Field(..., examples=["Video"])


class AIGenerateResponse(BaseModel):
    """Saída estruturada retornada pela IA."""

    # É o que a IA vai devolver. Forcei vir pelo menos 1 tag e no máximo 10 pra não virar bagunça.
    description: str = Field(..., description="Descrição gerada automaticamente pelo LLM")
    tags: List[str] = Field(..., min_length=1, max_length=10, description="Tags relevantes geradas")


class AIUsageMetrics(BaseModel):
    """Métricas de uso dos tokens Groq (para observabilidade)."""

    # Para controlar o gasto
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float  # Importante pra saber se a IA tá lenta demais
    model: str  # Pra gente saber qual versão do Llama a gente usou (caso mude depois)
