"""
Módulo de segurança da aplicação.

"""

import re

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ── Padrões de chaves que NUNCA devem aparecer em logs ou respostas ───────────
_SENSITIVE_PATTERNS = [
    re.compile(r"gsk_[a-zA-Z0-9]{40,}"),  # Groq API Key
    re.compile(r"sk-[a-zA-Z0-9]{40,}"),  # OpenAI API Key
    re.compile(r"Bearer\s+[a-zA-Z0-9\-_.]{20,}"),  # Bearer tokens
]


def mask_sensitive(text: str) -> str:
    """
    Mascara chaves e tokens sensíveis em strings antes de logar.

    """
    for pattern in _SENSITIVE_PATTERNS:
        text = pattern.sub("***MASKED***", text)
    return text


def validate_api_key_safety() -> None:
    """
    Valida que a chave Groq não está hardcoded ou exposta de forma insegura.
    Executado na inicialização da aplicação.
    """
    key = settings.GROQ_API_KEY

    if key.startswith("gsk_SUBSTITUA") or key == "sua_chave_aqui":
        logger.warning(
            "⚠️  ATENÇÃO: GROQ_API_KEY parece ser um valor de exemplo! "
            "Substitua pela chave real no arquivo .env",
        )

    # Loga apenas os primeiros 8 caracteres para confirmar carregamento
    masked_key = f"{key[:8]}{'*' * (len(key) - 8)}"
    logger.info(
        "🔐 API Key carregada com segurança",
        extra={"key_preview": masked_key, "source": ".env"},
    )
