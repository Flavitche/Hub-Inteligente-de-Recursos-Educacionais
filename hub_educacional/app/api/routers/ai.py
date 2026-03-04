import time

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import GroqAPIError
from app.core.logging import get_logger
from app.schemas.ai import AIGenerateRequest, AIGenerateResponse
from app.services.ai_service import GroqAIService, get_groq_service

# Configuração do log e do roteador do FastAPI
logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    response_model=AIGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Gerar descrição e tags via IA",
    description=(
        "Usa a API Groq para gerar automaticamente uma descrição pedagógica "
        "e tags relevantes com base no título e tipo do recurso educacional."
    ),
)
async def generate_ai_content(
    payload: AIGenerateRequest,
    service: GroqAIService = Depends(get_groq_service),
) -> AIGenerateResponse:

    # Timer pra gente medir a latência da API do Groq
    start_time = time.perf_counter()

    logger.info(
        f'AI Request iniciado: Title="{payload.title}", Type={payload.type.value}',
        extra={"title": payload.title, "type": payload.type.value},
    )

    try:
        # Chama o service que faz a mágica com o LLM
        ai_response, metrics = await service.generate_description_and_tags(payload)

    except GroqAPIError as exc:
        # Erro específico da API (ex: timeout, quota, chave inválida)
        latency_s = round((time.perf_counter() - start_time), 2)
        logger.error(
            f'AI Request falhou: Title="{payload.title}", '
            f"Latency={latency_s}s, Error={exc.message}",
            extra={
                "title": payload.title,
                "type": payload.type.value,
                "latency_s": latency_s,
                "error": exc.message,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao comunicar com serviço de IA: {exc.message}",
        )

    except Exception:
        # Catch-all para qualquer erro estranho que eu n previ
        logger.exception(
            f'AI Request erro inesperado: Title="{payload.title}"',
            extra={"title": payload.title, "type": payload.type.value},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar requisição de IA",
        )

    # Log de sucesso com as métricas de tokens e tempo (é bom pra monitorar custo)
    logger.info(
        f'AI Request concluído: Title="{payload.title}", '
        f"TokenUsage={metrics.total_tokens}, "
        f"Latency={metrics.latency_ms / 1000:.2f}s, "
        f"Tags={ai_response.tags}",
        extra={
            "title": payload.title,
            "type": payload.type.value,
            "total_tokens": metrics.total_tokens,
            "prompt_tokens": metrics.prompt_tokens,
            "completion_tokens": metrics.completion_tokens,
            "latency_ms": metrics.latency_ms,
            "tags_geradas": ai_response.tags,
            "model": metrics.model,
        },
    )

    return ai_response