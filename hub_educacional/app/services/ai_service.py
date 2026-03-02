"""
Serviço de integração com a API Groq (LLM).

Responsabilidades:
- Construção do System Prompt robusto
- Chamada HTTP para Groq via httpx (async)
- Parsing estrito do JSON retornado
- Logging de tokens e latência
- Retry com backoff exponencial
"""
import json
import re
import time
from typing import Any, Dict

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.exceptions import GroqAPIError
from app.core.logging import get_logger
from app.schemas.ai import AIGenerateRequest, AIGenerateResponse, AIUsageMetrics

logger = get_logger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é um especialista em educação digital e curadoria de conteúdo educacional.

Sua tarefa é analisar o título e o tipo de um recurso educacional e gerar:
1. Uma descrição clara, objetiva e informativa (entre 80 e 200 palavras)
2. Entre 3 e 7 tags relevantes em português, no singular, em letras minúsculas

REGRAS OBRIGATÓRIAS:
- Responda EXCLUSIVAMENTE com JSON válido, sem markdown, sem blocos de código, sem texto adicional
- O JSON deve seguir exatamente este schema:
  {
    "description": "<string com a descrição>",
    "tags": ["<tag1>", "<tag2>", ...]
  }
- A descrição deve ser educativa, mencionando o que o aluno aprenderá
- As tags devem ser palavras-chave úteis para busca e categorização
- Nunca adicione campos extras ao JSON
- Nunca use aspas simples, apenas duplas (JSON padrão)
- Não inclua nenhum texto antes ou depois do JSON

Exemplos de tags válidas: "python", "programação", "iniciante", "algoritmos", "machine learning"
"""


def _build_user_message(request: AIGenerateRequest) -> str:
    return (
        f"Gere a descrição e tags para o seguinte recurso educacional:\n\n"
        f"Título: {request.title}\n"
        f"Tipo: {request.type.value}"
    )


def _extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Extrai e valida o JSON da resposta do LLM.
    Tenta parsing direto primeiro; se falhar, tenta extrair bloco JSON via regex.
    """
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extrai primeiro bloco {...} via regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise GroqAPIError(f"LLM não retornou JSON válido. Resposta: {text[:200]!r}")


class GroqAIService:
    """
    Cliente assíncrono para a API Groq.
    Usa httpx.AsyncClient para não bloquear o event loop do FastAPI.
    """

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(30.0, connect=5.0),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def generate_description_and_tags(
        self, request: AIGenerateRequest
    ) -> tuple[AIGenerateResponse, AIUsageMetrics]:
        """
        Chama a API Groq e retorna descrição + tags + métricas de uso.
        Faz retry automático em caso de falhas transitórias (429, 503).
        """
        start_time = time.perf_counter()

        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_message(request)},
            ],
            "max_tokens": settings.GROQ_MAX_TOKENS,
            "temperature": settings.GROQ_TEMPERATURE,
            "response_format": {"type": "json_object"},  # Força JSON mode quando disponível
        }

        try:
            response = await self._client.post(GROQ_API_URL, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Erro HTTP na API Groq",
                extra={"status_code": exc.response.status_code, "body": exc.response.text[:500]},
            )
            raise GroqAPIError(
                f"Groq API retornou {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Erro de conexão com Groq API", extra={"error": str(exc)})
            raise GroqAPIError(f"Falha de conexão: {exc}") from exc

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        data = response.json()

        # ── Extrai conteúdo e métricas ────────────────────────────────────────
        raw_content: str = data["choices"][0]["message"]["content"]
        usage: Dict[str, int] = data.get("usage", {})

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        metrics = AIUsageMetrics(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            model=settings.GROQ_MODEL,
        )

        logger.info(
            "Groq API call concluída",
            extra={
                "model": settings.GROQ_MODEL,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency_ms,
            },
        )

        # ── Valida e parseia JSON ─────────────────────────────────────────────
        parsed = _extract_json_from_response(raw_content)

        if "description" not in parsed or "tags" not in parsed:
            raise GroqAPIError(
                f"JSON retornado não contém 'description' e/ou 'tags'. Recebido: {list(parsed.keys())}"
            )

        ai_response = AIGenerateResponse(
            description=str(parsed["description"]),
            tags=[str(t).strip().lower() for t in parsed["tags"] if str(t).strip()],
        )

        return ai_response, metrics


# ── Dependency Factory ─────────────────────────────────────────────────────────
async def get_groq_service() -> GroqAIService:
    """FastAPI dependency que provê o GroqAIService."""
    async with GroqAIService() as service:
        yield service