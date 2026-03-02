"""
Endpoint de saúde da aplicação.
Verifica conectividade com banco de dados e estado geral da API.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db

logger = get_logger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    environment: str
    timestamp: str
    database: str
    version: str
    uptime_check_ms: float


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    start = time.perf_counter()
    db_status = "ok"

    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Health check: falha no banco", extra={"error": str(exc)})
        db_status = "unavailable"

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return HealthResponse(
        status="healthy" if db_status == "ok" else "degraded",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        database=db_status,
        version="1.0.0",
        uptime_check_ms=elapsed_ms,
    )
