"""Puertos (interfaces) que la infraestructura implementa (ADR-009, SOLID-D)."""
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Protocol

from src.domain.repositorios import GuiaRepository, IncidenciaRepository


class UnitOfWork(ABC):
    """Un caso de uso = una transacción (ADR-005)."""

    guias: GuiaRepository
    incidencias: IncidenciaRepository

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, traza):
        if tipo is not None:
            self.rollback()

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...


class AlmacenEvidencias(Protocol):
    def guardar(self, numero_guia: str, firma: str, foto: str) -> str: ...


class PublicadorEventos(Protocol):
    def publicar(self, eventos: list) -> None: ...


class Reloj(Protocol):
    def ahora(self) -> datetime: ...


class RelojSistema:
    def ahora(self) -> datetime:
        return datetime.now(UTC)


class HistorialRastreoReader(Protocol):
    """Lado de lectura (CQRS, ADR-003)."""

    def estado_publico(self, numero: str) -> dict | None: ...
    def historial(self, numero: str) -> dict | None: ...
