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

connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # O SQLite por padrão não gosta de várias pessoas mexendo ao mesmo tempo,
    # essa linha libera isso pra o FastAPI não travar.
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Se eu quiser ver o SQL puro que o Python cria, mudo pra True
    pool_pre_ping=True,  # Dá uma "cutucada" na conexão antes de usar pra ver se tá viva
)

if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        # WAL deixa o banco mais rápido pra ler e escrever ao mesmo tempo
        cursor.execute("PRAGMA journal_mode=WAL")
        # Garante que se eu deletar algo, as chaves estrangeiras funcionem (não fique lixo no banco)
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# É o "molde" das sessões. O expire_on_commit=False é pra eu conseguir ler o objeto
# mesmo depois de salvar no banco, sem dar erro de sessão fechada.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── Base Declarativa ───────────────────────────────────────────────────────────
# Todo Model (tabela) que eu criar vai herdar dessa classe aqui
class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency do FastAPI que provê uma sessão de banco por request.
    """
    db = SessionLocal()
    try:
        yield db  # Entrega a conexão pro endpoint usar
    except Exception:
        db.rollback()  # Se der ruim cancela tudo que ia ser salvo pra não corromper
        raise
    finally:
        db.close()  # No final de tudo, sempre fecha a porta pra não gastar memória
