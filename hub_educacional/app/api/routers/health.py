"""
Endpoint de saúde da aplicação.
Verifica conectividade com banco de dados e também estado geral da API.
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


# Schema de resposta pra bater com o que o monitoramento (Prometheus/UptimeRobot) espera
class HealthResponse(BaseModel):
    status: str
    environment: str
    timestamp: str
    database: str
    version: str
    uptime_check_ms: float


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    # Inicia o timer pra medir a latência interna do sistema
    start = time.perf_counter()
    db_status = "ok"

    try:
        # Só um "ping" no banco pra ver se a conexão tá viva
        db.execute(text("SELECT 1"))
    except Exception as exc:
        # Se o banco cair, a gente loga o erro mas não deixa o endpoint quebrar 100%
        logger.error("Health check: falha no banco", extra={"error": str(exc)})
        db_status = "unavailable"

    # Calcula quanto tempo levou esse checkup em milissegundos
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return HealthResponse(
        # Se o banco tá fora, o status vira "degraded" (alerta pro monitoramento)
        status="healthy" if db_status == "ok" else "degraded",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        database=db_status,
        version="1.0.0",
        uptime_check_ms=elapsed_ms,
    )
