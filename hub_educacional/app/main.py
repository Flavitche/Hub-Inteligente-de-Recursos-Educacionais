"""
Hub Inteligente de Recursos Educacionais
Entry point da aplicação FastAPI.
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import resources, ai, health
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import engine, Base

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação."""
    logger.info("🚀 Iniciando Hub Inteligente de Recursos Educacionais", extra={"env": settings.ENVIRONMENT})
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Banco de dados inicializado com sucesso")
    yield
    logger.info("🛑 Encerrando aplicação")


app = FastAPI(
    title="Hub Inteligente de Recursos Educacionais",
    description="API para gerenciamento e geração inteligente de recursos educacionais",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# ── Middlewares ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Loga cada requisição com latência."""
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    logger.info(
        "HTTP request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        },
    )
    response.headers["X-Process-Time-Ms"] = str(latency_ms)
    return response


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Observabilidade"])
app.include_router(resources.router, prefix="/resources", tags=["Recursos"])
app.include_router(ai.router, prefix="/ai", tags=["Inteligência Artificial"])


# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})