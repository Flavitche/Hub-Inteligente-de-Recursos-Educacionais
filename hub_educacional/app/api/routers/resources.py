"""
Router FastAPI para CRUD de Recursos Educacionais.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_db
from app.schemas.resource import (
    PaginatedResponse,
    ResourceCreate,
    ResourceResponse,
    ResourceType,
    ResourceUpdate,
)
from app.services.resource_service import ResourceService

router = APIRouter()


# Injeta a sessão do banco no service pra centralizar a lógica de dados
def get_resource_service(db: Session = Depends(get_db)) -> ResourceService:
    return ResourceService(db)


# Alias pra facilitar o uso do service nos endpoints e ficar mais limpo
ServiceDep = Annotated[ResourceService, Depends(get_resource_service)]


@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(payload: ResourceCreate, service: ServiceDep):
    return service.create(payload)


@router.get("/", response_model=PaginatedResponse[ResourceResponse])
def list_resources(
    service: ServiceDep,
    page: int = Query(default=1, ge=1),  # Validação pra não vir página 0 ou negativa
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    type: Optional[ResourceType] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    search: Optional[str] = Query(
        default=None, min_length=2
    ),  # Evita buscas vazias ou curtas demais
):
    # Separa os itens do total pra montar a paginação correta no front
    items, total = service.list_resources(
        page=page,
        page_size=page_size,
        type_filter=type.value if type else None,
        tag_filter=tag,
        search=search,
    )
    return PaginatedResponse.create(
        items=[ResourceResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, service: ServiceDep):
    try:
        return service.get_by_id(resource_id)
    except ResourceNotFoundError as exc:
        # Erro 404 padrão se o ID não existir no banco
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.patch("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, payload: ResourceUpdate, service: ServiceDep):
    try:
        # Patch permite atualização parcial (só o que foi enviado no body)
        return service.update(resource_id, payload)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, service: ServiceDep):
    try:
        service.delete(resource_id)
        # 204 indica que deu tudo certo, mas não tem conteúdo pra retornar
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
