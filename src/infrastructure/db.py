from datetime import UTC

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.infrastructure.modelos import Base


def crear_engine(url: str):
    if url.startswith("sqlite"):
        from sqlalchemy.pool import StaticPool
        extra = {"poolclass": StaticPool} if ":memory:" in url else {}
        engine = create_engine(url, connect_args={"check_same_thread": False}, **extra)
    else:
        engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return engine


def crear_fabrica_sesiones(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)


def como_utc(valor):
    """SQLite no guarda zona horaria: se interpreta como UTC al leer."""
    if valor is not None and valor.tzinfo is None:
        return valor.replace(tzinfo=UTC)
    return valor


__all__ = ["crear_engine", "crear_fabrica_sesiones", "como_utc", "event"]
