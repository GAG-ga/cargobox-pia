"""Domain Events (ADR-004): hechos del negocio que otros pueden escuchar."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EventoDominio:
    referencia: str
    ocurrido_en: datetime


@dataclass(frozen=True)
class GuiaGenerada(EventoDominio):
    pass


@dataclass(frozen=True)
class EstadoCambiado(EventoDominio):
    estado: str


@dataclass(frozen=True)
class IntentoEntregaFallido(EventoDominio):
    numero_intento: int


@dataclass(frozen=True)
class GuiaEnResguardo(EventoDominio):
    pass


@dataclass(frozen=True)
class EntregaCompletada(EventoDominio):
    pass


@dataclass(frozen=True)
class DireccionCambiada(EventoDominio):
    pass


@dataclass(frozen=True)
class PerdidaDeclarada(EventoDominio):
    compensacion: str


@dataclass(frozen=True)
class AlertaGenerada(EventoDominio):
    numero_guia: str


@dataclass(frozen=True)
class IncidenciaEscalada(EventoDominio):
    numero_guia: str
