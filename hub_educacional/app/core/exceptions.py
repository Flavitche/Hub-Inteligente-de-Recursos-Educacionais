"""
Exceções de domínio da aplicação.
Centralizar aqui facilita tratamento consistente em toda a API.
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base para todas as exceções da aplicação."""

    # Criei essa classe pai pra não ter que ficar repetindo 'message' e 'detail' em todo erro novo
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail or {}


class ResourceNotFoundError(AppError):
    """Recurso não encontrado no banco de dados."""

    # específico pra quando o ID que o usuário mandou não existe no banco
    def __init__(self, resource_id: int):
        super().__init__(
            f"Recurso com id={resource_id} não encontrado",
            {"resource_id": resource_id},
        )


class GroqAPIError(AppError):
    """Falha na chamada à API Groq."""

    # Se a IA der algum erro (tipo API fora do ar), eu uso esse pra guardar o código do erro
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, {"groq_status_code": status_code})


class InvalidPaginationError(AppError):
    """Parâmetros de paginação inválidos."""

    # Se alguém tentar pedir a página -1 ou algo bizarro, a gente joga esse erro aqui
