"""
Exceções de domínio da aplicação.
Centralizar aqui facilita tratamento consistente em toda a API.
"""
from typing import Any, Dict, Optional


class AppError(Exception):
    """Base para todas as exceções da aplicação."""

    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail or {}


class ResourceNotFoundError(AppError):
    """Recurso não encontrado no banco de dados."""

    def __init__(self, resource_id: int):
        super().__init__(
            f"Recurso com id={resource_id} não encontrado",
            {"resource_id": resource_id},
        )


class GroqAPIError(AppError):
    """Falha na chamada à API Groq."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, {"groq_status_code": status_code})


class InvalidPaginationError(AppError):
    """Parâmetros de paginação inválidos."""