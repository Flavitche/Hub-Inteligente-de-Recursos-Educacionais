"""
Modelo SQLAlchemy para Recursos Educacionais.
Usa JSON nativo para o campo tags (compatível com SQLite e PostgreSQL).
"""

import json
from datetime import datetime, timezone
from typing import List

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String, Text, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.schemas.resource import ResourceType


class JSONList(TypeDecorator):
    """
    Tipo customizado que persiste List[str] como JSON string.
    Compatível com SQLite (sem suporte nativo a ARRAY) e PostgreSQL.
    Para PostgreSQL em produção, prefira usar ARRAY ou JSONB nativamente.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        if not value:
            return []
        return json.loads(value)


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


class Resource(Base):
    """
    Tabela principal de recursos educacionais.

    Campos:
    - id: PK auto-incrementada
    - title: Título obrigatório (max 255 chars)
    - description: Descrição longa opcional
    - type: Enum restrito a Video, PDF, Link
    - url: URL do recurso (max 2048 chars)
    - tags: Lista de strings armazenada como JSON
    - created_at / updated_at: Timestamps automáticos (UTC)
    """

    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(
        SAEnum(ResourceType, name="resource_type", native_enum=False),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSONList, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now_utc,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now_utc,
        onupdate=_now_utc,
    )

    def __repr__(self) -> str:
        return f"<Resource id={self.id} title={self.title!r} type={self.type}>"
