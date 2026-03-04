"""
Módulo de segurança da aplicação.
"""

import re
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Criei esses "moldes" (regex) pra identificar automaticamente chaves da Groq, OpenAI ou Tokens
_SENSITIVE_PATTERNS = [
    re.compile(r"gsk_[a-zA-Z0-9]{40,}"),  # Groq API Key
    re.compile(r"sk-[a-zA-Z0-9]{40,}"),  # OpenAI API Key
    re.compile(r"Bearer\s+[a-zA-Z0-9\-_.]{20,}"),  # Bearer tokens
]


def mask_sensitive(text: str) -> str:
    """
    Mascara chaves e tokens sensíveis em strings antes de logar.
    """
    # Se alguma das chaves acima aparecer no texto, eu troco por ***MASKED***
    for pattern in _SENSITIVE_PATTERNS:
        text = pattern.sub("***MASKED***", text)
    return text


def validate_api_key_safety() -> None:
    """
    Valida que a chave Groq não está hardcoded ou exposta de forma insegura.
    Executado na inicialização da aplicação.
    """
    key = settings.GROQ_API_KEY

    # Check básico pra eu não subir o código com a chave de exemplo
    if key.startswith("gsk_SUBSTITUA") or key == "sua_chave_aqui":
        logger.warning(
            "⚠️  ATENÇÃO: GROQ_API_KEY parece ser um valor de exemplo! "
            "Substitua pela chave real no arquivo .env",
        )

    # Mostro só o comecinho da chave no log pra eu saber que carregou a certa,
    # mas escondo o resto pra não vazar minha conta
    masked_key = f"{key[:8]}{'*' * (len(key) - 8)}"
    logger.info(
        "🔐 API Key carregada com segurança",
        extra={"key_preview": masked_key, "source": ".env"},
    )
