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

    impl = Text
    cache_ok = True

    # Esse aqui prepara o dado pra salvar: transforma a lista de Python em uma string JSON
    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value, ensure_ascii=False)

    # Esse aqui faz o contrário: quando eu leio do banco, ele transforma a string de volta em lista
    def process_result_value(self, value, dialect):
        if not value:
            return []
        return json.loads(value)


# sempre usar o horário de Brasília/UTC padrão e não o da máquina
def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


class Resource(Base):
    """
    Tabela principal de recursos educacionais no banco.
    """

    __tablename__ = "resources"

    # PK básica com index pra busca ser rápida
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # String(255) pra não deixar o título ser infinito
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Text é melhor que String pra descrição porque cabe muito mais coisa
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Aqui eu uso o Enum que a gente criou nos schemas pra limitar o que pode ser salvo
    type: Mapped[str] = mapped_column(
        SAEnum(ResourceType, name="resource_type", native_enum=False),
        nullable=False,
        index=True,
    )

    url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # Uso minha classe JSONList pra conseguir salvar uma lista no SQLite
    tags: Mapped[List[str]] = mapped_column(JSONList, nullable=False, default=list)

    # Datas automáticas: uma fixa o nascimento do registro e a outra atualiza sozinha no 'save'
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

    # Pra quando eu der um 'print(resource)' no terminal, aparecer algo que dê pra ler
    def __repr__(self) -> str:
        return f"<Resource id={self.id} title={self.title!r} type={self.type}>"
