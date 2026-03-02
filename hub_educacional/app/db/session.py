"""
Configuração do SQLAlchemy: engine, session factory e Base declarativa.
Suporta PostgreSQL e SQLite (útil para testes e desenvolvimento local).
"""

from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Engine ─────────────────────────────────────────────────────────────────────
connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite precisa de check_same_thread=False para uso com FastAPI (threads múltiplas)
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # True para debug de queries SQL
    pool_pre_ping=True,  # Verifica conexão antes de usar (evita stale connections)
    # Para PostgreSQL em produção, adicione:
    # pool_size=10,
    # max_overflow=20,
)

# ── SQLite WAL mode para melhor concorrência ───────────────────────────────────
if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ── Session Factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Evita lazy-loading após commit
)


# ── Base Declarativa ───────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency Injection ───────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Dependency do FastAPI que provê uma sessão de banco por request.
    A sessão é fechada automaticamente ao término da requisição.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
