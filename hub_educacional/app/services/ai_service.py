"""
Serviço de integração com a API Groq (LLM).
Usa recursos modernos do Python: dataclasses, decorators, type hints avançados.
"""

import functools
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import GroqAPIError
from app.core.logging import get_logger
from app.schemas.ai import AIGenerateRequest, AIGenerateResponse, AIUsageMetrics

logger = get_logger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# Dataclass pra representar o resultado bruto da Groq
@dataclass(frozen=True, slots=True)
class GroqRawResult:
    """Resultado bruto e imutável retornado pela API Groq."""

    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    model: str

    @property
    def latency_s(self) -> float:
        return round(self.latency_ms / 1000, 2)


# Dataclass para contexto de tipo do recurso
@dataclass(frozen=True, slots=True)
class ResourceTypeContext:
    """Contexto pedagógico enriquecido por tipo de recurso."""

    label: str
    learning_style: str
    best_for: str


RESOURCE_TYPE_CONTEXTS: Dict[str, ResourceTypeContext] = {
    "Video": ResourceTypeContext(
        label="Vídeo Educacional",
        learning_style="aprendizado visual e auditivo",
        best_for="explicações dinâmicas, demonstrações práticas e tutoriais passo a passo",
    ),
    "PDF": ResourceTypeContext(
        label="Documento PDF",
        learning_style="leitura aprofundada e estudo estruturado",
        best_for="apostilas, e-books, resumos e materiais de referência",
    ),
    "Link": ResourceTypeContext(
        label="Link Externo",
        learning_style="exploração interativa e leitura complementar",
        best_for="artigos, documentações oficiais e recursos online especializados",
    ),
}


# Decorator de logging de performance
def log_ai_call(func: Callable) -> Callable:
    """
    Decorator moderno que loga automaticamente início, fim e erros
    de qualquer chamada assíncrona à IA.
    """

    @functools.wraps(func)
    async def wrapper(self, request: AIGenerateRequest, *args, **kwargs):
        logger.info(
            f'[AI] Iniciando geração | Title="{request.title}" | Type={request.type.value}',
            extra={"title": request.title, "type": request.type.value},
        )
        start = time.perf_counter()
        try:
            result = await func(self, request, *args, **kwargs)
            elapsed = round(time.perf_counter() - start, 2)
            logger.info(
                f'[AI] Geração concluída | Title="{request.title}" | Latency={elapsed}s',
                extra={"title": request.title, "latency_s": elapsed},
            )
            return result
        except Exception as exc:
            elapsed = round(time.perf_counter() - start, 2)
            logger.error(
                f'[AI] Falha na geração | Title="{request.title}" | '
                f"Latency={elapsed}s | Error={exc}",
                extra={"title": request.title, "latency_s": elapsed, "error": str(exc)},
            )
            raise

    return wrapper


# ── System Prompt — Assistente Pedagógico ─────────────────────────────────────
SYSTEM_PROMPT = """Você é um Assistente Pedagógico especializado em educação digital e curadoria de conteúdo educacional.

Seu papel é ajudar alunos e educadores a compreenderem rapidamente o valor e o conteúdo de recursos educacionais, gerando descrições claras, motivadoras e pedagogicamente ricas.

═══════════════════════════════════════
PERSONA — ASSISTENTE PEDAGÓGICO:
═══════════════════════════════════════
- Você fala diretamente COM O ALUNO, não sobre o recurso
- Use linguagem acolhedora, motivadora e acessível
- Seu objetivo é despertar o interesse do aluno pelo conteúdo
- Demonstre entusiasmo pelo aprendizado sem exageros
- Seja específico: o aluno deve saber EXATAMENTE o que vai aprender

═══════════════════════════════════════
DIRETRIZES PARA A DESCRIÇÃO (100-220 palavras):
═══════════════════════════════════════
1. ABERTURA: Frase de impacto que conecta o conteúdo à realidade do aluno
2. CONTEÚDO: O que o aluno vai aprender de forma concreta e específica
3. NÍVEL: Indique quando inferível (iniciante / intermediário / avançado)
4. PRÁTICA: Como o conhecimento pode ser aplicado no mundo real
5. FECHAMENTO: Frase motivadora que incentive o aluno a começar agora
- NUNCA invente informações que não possam ser inferidas pelo título
- NUNCA use jargões pedagógicos desnecessários

═══════════════════════════════════════
DIRETRIZES PARA AS TAGS (4 a 7 tags):
═══════════════════════════════════════
- Palavras-chave úteis para busca e categorização
- Sempre em português, singular e letras minúsculas
- Inclua: área principal, subtópicos relevantes, nível quando claro
- Ordene da mais relevante para a menos relevante
- Evite tags genéricas como "curso", "aula", "aprendizado"

═══════════════════════════════════════
FORMATO DE RESPOSTA — OBRIGATÓRIO:
═══════════════════════════════════════
Responda EXCLUSIVAMENTE com JSON válido. Sem markdown, sem blocos de código, sem texto adicional.

{
  "description": "<descrição pedagógica entre 100 e 220 palavras>",
  "tags": ["<tag1>", "<tag2>", "<tag3>", "<tag4>"]
}

REGRAS CRÍTICAS:
- Apenas aspas duplas (JSON padrão)
- Nenhum campo extra além de "description" e "tags"
- Nenhum texto fora do JSON
- JSON parseável diretamente por json.loads()
"""


def _build_user_message(request: AIGenerateRequest) -> str:
    """Constrói mensagem enriquecida com contexto pedagógico do tipo de recurso."""
    ctx = RESOURCE_TYPE_CONTEXTS.get(
        request.type.value,
        ResourceTypeContext(
            label=request.type.value, learning_style="geral", best_for="aprendizado"
        ),
    )
    return (
        f"Gere a descrição pedagógica e as tags para o seguinte recurso educacional:\n\n"
        f"Título: {request.title}\n"
        f"Tipo: {ctx.label}\n"
        f"Estilo de aprendizado: {ctx.learning_style}\n"
        f"Ideal para: {ctx.best_for}\n\n"
        f"Lembre-se: você é um Assistente Pedagógico falando diretamente com o aluno. "
        f"Responda apenas com JSON válido."
    )


def _extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extrai e valida JSON da resposta do LLM com fallback via regex."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

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
    Usa recursos modernos do Python: dataclasses, decorators, slots, frozen.
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

    @log_ai_call
    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def generate_description_and_tags(
        self, request: AIGenerateRequest
    ) -> tuple[AIGenerateResponse, AIUsageMetrics]:

        start_time = time.perf_counter()

        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_message(request)},
            ],
            "max_tokens": settings.GROQ_MAX_TOKENS,
            "temperature": settings.GROQ_TEMPERATURE,
            "response_format": {"type": "json_object"},
        }

        try:
            response = await self._client.post(GROQ_API_URL, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Erro HTTP na API Groq",
                extra={
                    "status_code": exc.response.status_code,
                    "body": exc.response.text[:500],
                },
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

        raw_content: str = data["choices"][0]["message"]["content"]
        usage: Dict[str, int] = data.get("usage", {})

        raw_result = GroqRawResult(
            content=raw_content,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
            model=settings.GROQ_MODEL,
        )

        # Log estruturado
        logger.info(
            f'[INFO] AI Request: Title="{request.title}", '
            f"TokenUsage={raw_result.total_tokens}, "
            f"Latency={raw_result.latency_s}s",
            extra={
                "title": request.title,
                "type": request.type.value,
                "model": raw_result.model,
                "prompt_tokens": raw_result.prompt_tokens,
                "completion_tokens": raw_result.completion_tokens,
                "total_tokens": raw_result.total_tokens,
                "latency_ms": raw_result.latency_ms,
                "latency_s": raw_result.latency_s,
            },
        )

        parsed = _extract_json_from_response(raw_result.content)

        if "description" not in parsed or "tags" not in parsed:
            raise GroqAPIError(
                f"JSON retornado não contém 'description' e/ou 'tags'. "
                f"Recebido: {list(parsed.keys())}"
            )

        metrics = AIUsageMetrics(
            prompt_tokens=raw_result.prompt_tokens,
            completion_tokens=raw_result.completion_tokens,
            total_tokens=raw_result.total_tokens,
            latency_ms=raw_result.latency_ms,
            model=raw_result.model,
        )

        ai_response = AIGenerateResponse(
            description=str(parsed["description"]),
            tags=[str(t).strip().lower() for t in parsed["tags"] if str(t).strip()],
        )

        return ai_response, metrics


async def get_groq_service() -> GroqAIService:
    async with GroqAIService() as service:
        yield service
