"""
Schemas Pydantic para validação e serialização de Recursos.

Separação clara de responsabilidades:
- ResourceCreate: dados para criação (sem id/timestamps)
- ResourceUpdate: todos os campos opcionais (PATCH semântico)
- ResourceResponse: shape de saída da API
- PaginatedResponse: wrapper genérico para listagens paginadas
"""

from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class ResourceType(str, Enum):
    VIDEO = "Video"
    PDF = "PDF"
    LINK = "Link"


# ── Base ───────────────────────────────────────────────────────────────────────
class ResourceBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, examples=["Introdução ao Python"])
    description: Optional[str] = Field(None, max_length=5000)
    type: ResourceType
    url: AnyHttpUrl = Field(..., examples=["https://youtube.com/watch?v=example"])
    tags: List[str] = Field(default_factory=list, max_length=20)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: List[str]) -> List[str]:
        cleaned = []
        seen = set()
        for tag in tags:
            tag = tag.strip().lower()
            if not tag:
                continue
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag[:20]}...' excede 50 caracteres")
            if tag not in seen:
                seen.add(tag)
                cleaned.append(tag)
        return cleaned

    @field_validator("url", mode="before")
    @classmethod
    def url_to_string(cls, v) -> str:
        return str(v)


# ── Create ─────────────────────────────────────────────────────────────────────
class ResourceCreate(ResourceBase):
    """Payload de criação de recurso. Todos os campos base são obrigatórios."""

    pass


# ── Update ─────────────────────────────────────────────────────────────────────
class ResourceUpdate(BaseModel):
    """
    Payload de atualização parcial (PATCH).
    Todos os campos são opcionais — apenas os enviados são alterados.
    """

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    type: Optional[ResourceType] = None
    url: Optional[AnyHttpUrl] = None
    tags: Optional[List[str]] = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: Optional[List[str]]) -> Optional[List[str]]:
        if tags is None:
            return None
        cleaned, seen = [], set()
        for tag in tags:
            tag = tag.strip().lower()
            if tag and tag not in seen:
                seen.add(tag)
                cleaned.append(tag)
        return cleaned

    @field_validator("url", mode="before")
    @classmethod
    def url_to_string(cls, v) -> Optional[str]:
        return str(v) if v is not None else None


# ── Response ───────────────────────────────────────────────────────────────────
class ResourceResponse(ResourceBase):
    """Shape de resposta da API — inclui campos gerados pelo servidor."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ── Paginação ──────────────────────────────────────────────────────────────────
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, page_size: int
    ) -> "PaginatedResponse[T]":
        total_pages = max(1, -(-total // page_size))  # ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
