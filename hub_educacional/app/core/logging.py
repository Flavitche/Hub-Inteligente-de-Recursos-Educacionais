"""
Logging estruturado com formato JSON para ambientes de produção
e formato legível para desenvolvimento.
"""

import logging
import sys
from datetime import datetime, timezone

from app.core.config import settings

class StructuredFormatter(logging.Formatter):
    """Formata logs como JSON estruturado."""

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_entry = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Essa lista serve pra filtrar o que é "sujeira" do Python 
        # e pegar só os dados extras que eu realmente passei no log
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "taskName",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_entry[key] = value

        # Se o código quebrar, anexa o erro (traceback) dentro do JSON
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)
class PrettyFormatter(logging.Formatter):
    """Formato legível para desenvolvimento."""

    # Cores pra eu bater o olho no terminal e saber logo o que é erro
    COLORS = {
        "DEBUG": "\033[36m",    # Ciano
        "INFO": "\033[32m",     # Verde
        "WARNING": "\033[33m",  # Amarelo
        "ERROR": "\033[31m",    # Vermelho
        "CRITICAL": "\033[35m", # Roxo
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        ts = datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
        
        base = (
            f"{color}[{ts}] {record.levelname:<8}{self.RESET} {record.name} | {record.getMessage()}"
        )

        # Se eu passei info extra (tipo ID de usuário), anexa no final da linha
        extras = {k: v for k, v in record.__dict__.items() if k not in self._get_std_attrs()}
        if extras:
            base += f" | {extras}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base

    def _get_std_attrs(self):
        # Mesma lista de atributos padrão pra não repetir lá em cima
        return {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "taskName",
        }


def setup_logging() -> None:
    """Configura o sistema de logging global."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Limpa as configs padrão pra não imprimir o log duas vezes
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.ENVIRONMENT == "production":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(PrettyFormatter())

    root_logger.addHandler(handler)

    # Abaixa o volume de bibliotecas que logam demais e atrapalham o debug
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado (use __name__ como convenção)."""
    setup_logging()
    return logging.getLogger(name)