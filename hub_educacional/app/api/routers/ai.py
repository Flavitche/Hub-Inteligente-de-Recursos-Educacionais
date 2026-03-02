"""
Router FastAPI para geração de conteúdo via IA (Groq LLM).

Endpoints:
  POST /ai/generate - Gera descrição e tags para um recurso educacional
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import GroqAPIError
from app.core.logging import get_logger
from app.schemas.ai import AIGenerateRequest, AIGenerateResponse
from app.services.ai_service import GroqAIService, get_groq_service

logger = get_logger(__name__)
router = APIRouter()


@router.post("/generate", response_model=AIGenerateResponse, status_code=status.HTTP_200_OK)
async def generate_ai_content(
    payload: AIGenerateRequest,
    service: GroqAIService = Depends(get_groq_service),
) -> AIGenerateResponse:
    try:
        ai_response, metrics = await service.generate_description_and_tags(payload)
    except GroqAPIError as exc:
        logger.error(
            "Falha na geração via IA",
            extra={"title": payload.title, "type": payload.type, "error": exc.message},
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com serviço de IA: {exc.message}",
        )
    except Exception:
        logger.exception("Erro inesperado no endpoint de IA")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar requisição de IA",
        )

    logger.info(
        "Geração de IA concluída",
        extra={
            "title": payload.title,
            "tags_count": len(ai_response.tags),
            "total_tokens": metrics.total_tokens,
            "latency_ms": metrics.latency_ms,
        },
    )

    return ai_response