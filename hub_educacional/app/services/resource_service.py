"""
Service layer para Recursos Educacionais.

Responsabilidades:
- Lógica de negócio (ex: validações de domínio)
- Interação com o banco via SQLAlchemy
- Tratamento de erros de domínio
- Nunca acessa HTTP diretamente — puro Python/SQLAlchemy
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.core.logging import get_logger
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate

logger = get_logger(__name__)


class ResourceService:
    """
    Serviço de CRUD para Recursos Educacionais.
    Instanciado por request (injeção de dependência via FastAPI).
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── CREATE ─────────────────────────────────────────────────────────────────
    def create(self, payload: ResourceCreate) -> Resource:
        resource = Resource(
            title=payload.title,
            description=payload.description,
            type=payload.type,
            url=str(payload.url),
            tags=payload.tags,
        )
        self._db.add(resource)
        self._db.commit()
        self._db.refresh(resource)
        logger.info("Recurso criado", extra={"resource_id": resource.id, "type": resource.type})
        return resource

    # ── READ (single) ──────────────────────────────────────────────────────────
    def get_by_id(self, resource_id: int) -> Resource:
        stmt = select(Resource).where(Resource.id == resource_id)
        resource = self._db.execute(stmt).scalar_one_or_none()
        if resource is None:
            raise ResourceNotFoundError(resource_id)
        return resource

    # ── READ (list + pagination) ───────────────────────────────────────────────
    def list_resources(
        self,
        page: int,
        page_size: int,
        type_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Resource], int]:
        """
        Retorna (itens_da_página, total_de_registros).
        Suporta filtros por tipo, tag e busca textual no título/descrição.
        """
        stmt = select(Resource)

        if type_filter:
            stmt = stmt.where(Resource.type == type_filter)

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                Resource.title.ilike(pattern) | Resource.description.ilike(pattern)
            )

        if tag_filter:
            # Busca por substring no JSON de tags (compatível com SQLite e PostgreSQL)
            stmt = stmt.where(Resource.tags.contains(tag_filter))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = self._db.execute(count_stmt).scalar_one()

        stmt = stmt.order_by(Resource.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list(self._db.execute(stmt).scalars().all())

        return items, total

    # ── UPDATE ─────────────────────────────────────────────────────────────────
    def update(self, resource_id: int, payload: ResourceUpdate) -> Resource:
        resource = self.get_by_id(resource_id)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            logger.warning("Update chamado sem campos para alterar", extra={"resource_id": resource_id})
            return resource

        for field, value in update_data.items():
            if field == "url" and value is not None:
                value = str(value)
            setattr(resource, field, value)

        resource.updated_at = datetime.now(tz=timezone.utc)
        self._db.commit()
        self._db.refresh(resource)
        logger.info(
            "Recurso atualizado",
            extra={"resource_id": resource_id, "fields_updated": list(update_data.keys())},
        )
        return resource

    # ── DELETE ─────────────────────────────────────────────────────────────────
    def delete(self, resource_id: int) -> None:
        resource = self.get_by_id(resource_id)
        self._db.delete(resource)
        self._db.commit()
        logger.info("Recurso deletado", extra={"resource_id": resource_id})