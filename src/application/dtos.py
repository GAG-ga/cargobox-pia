"""DTOs: lo que devuelven los casos de uso (nunca la entidad)."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GuiaDTO:
    numero: str
    estado: str
    nivel: str
    tarifa: str
    fecha_estimada: date
    destino: str
    intentos_fallidos: int
    con_garantia: bool
    cargos_adicionales: str
    reembolso: str
    compensacion: str
    mensaje: str


@dataclass(frozen=True)
class IncidenciaDTO:
    folio: str
    numero_guia: str
    tipo: str
    estado: str
    asignada_a: str
    resolucion: str | None


@dataclass(frozen=True)
class ResumenMonitoreoDTO:
    alertas_generadas: list[str]
    alertas_escaladas: list[str]
    guias_devueltas: list[str]
