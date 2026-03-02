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

        # Adiciona campos extras (passados via extra={})
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "taskName",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class PrettyFormatter(logging.Formatter):
    """Formato legível para desenvolvimento."""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        ts = datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
        base = f"{color}[{ts}] {record.levelname:<8}{self.RESET} {record.name} | {record.getMessage()}"

        extras = {}
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "taskName",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                extras[key] = value

        if extras:
            base += f" | {extras}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


def setup_logging() -> None:
    """Configura o sistema de logging global."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Remove handlers existentes para evitar duplicação
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.ENVIRONMENT == "production":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(PrettyFormatter())

    root_logger.addHandler(handler)

    # Silencia loggers muito verbosos de terceiros
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado (use __name__ como convenção)."""
    setup_logging()
    return logging.getLogger(name)