"""
Schemas Pydantic para validação e serialização de Recursos.
"""

from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


# Opções fixas pra não aceitarem qualquer texto no tipo de recurso
class ResourceType(str, Enum):
    VIDEO = "Video"
    PDF = "PDF"
    LINK = "Link"


class ResourceBase(BaseModel):
    # Regras básicas: título tem que ter tamanho mínimo e URL tem que ser válida
    title: str = Field(..., min_length=3, max_length=255, examples=["Introdução ao Python"])
    description: Optional[str] = Field(None, max_length=5000)
    type: ResourceType
    url: AnyHttpUrl = Field(..., examples=["https://youtube.com/watch?v=example"])
    tags: List[str] = Field(default_factory=list, max_length=20)

    # Limpeza automática: deixa as tags em minúsculo, tira espaços e remove repetidas
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

    # Garante que a URL vire uma string comum pra não dar erro de tipo depois
    @field_validator("url", mode="before")
    @classmethod
    def url_to_string(cls, v) -> str:
        return str(v)


# Create
class ResourceCreate(ResourceBase):
    """Payload de criação: herda tudo da base e exige os campos."""

    pass


# Update
class ResourceUpdate(BaseModel):
    """
    Pra atualizar, nada é obrigatório. Só muda o que o usuário mandar.
    """

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    type: Optional[ResourceType] = None
    url: Optional[AnyHttpUrl] = None
    tags: Optional[List[str]] = None

    # Mesma lógica de limpar tags que usamos na criação
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


class ResourceResponse(ResourceBase):
    """O que a API devolve: inclui os campos que o banco gera sozinho (ID e datas)."""

    # Esse comando é mágico: deixa o Pydantic ler os dados direto do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Paginação
T = TypeVar("T")


# Estrutura padrão pra quando a gente listar vários itens de uma vez
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
        # Cálculo pra saber quantas páginas existem no total (arredonda pra cima)
        total_pages = max(1, -(-total // page_size))
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
