"""Operación de servicio de paquete: modelo del paquete de datos del docente (datos/*.csv).

El paquete de pruebas del curso describe CargoBox como "operaciones" de un remitente con
líneas de servicios del catálogo. Este módulo traduce ese modelo a nuestro dominio:

* Los cambios de estado usan la MISMA máquina de estados de la guía (MaquinaEstadosGuia, ADR-007).
* Las reglas del paquete son Specifications combinadas con & | ~ (ADR-006).
* Cada cambio de estado publica el evento de dominio EstadoCambiado (ADR-004).

Las diferencias con el BRD del equipo están documentadas en docs/paquete-docente.md.
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from src.domain.errores import DatoInvalido, OperacionNoProcesable
from src.domain.especificaciones import Specification
from src.domain.estados import EstadoGuia, MaquinaEstadosGuia
from src.domain.eventos import EntregaCompletada, EstadoCambiado, EventoDominio
from src.domain.value_objects import Dinero

E = EstadoGuia
UMBRAL_BENEFICIO = Dinero(Decimal("1500"))
# Recorrido completo de nuestro BRD (§9.1) para "completar" una operación.
RUTA_COMPLETA = (E.CLASIFICADO, E.EN_TRANSITO, E.CENTRO_DESTINO, E.EN_REPARTO, E.ENTREGADO)


@dataclass(frozen=True)
class Remitente:
    actor_id: str
    activo: bool
    preferente: bool


@dataclass(frozen=True)
class ServicioCatalogo:
    recurso_id: str
    descripcion: str
    precio: Dinero
    capacidad: int
    habilitado: bool


@dataclass(frozen=True)
class LineaOperacion:
    servicio: ServicioCatalogo
    cantidad: int

    def __post_init__(self):
        if self.cantidad <= 0:
            raise DatoInvalido(f"La cantidad de {self.servicio.recurso_id} debe ser mayor a cero.")

    @property
    def subtotal(self) -> Dinero:
        return self.servicio.precio.por(self.cantidad)


@dataclass
class OperacionServicio:
    operacion_id: str
    remitente: Remitente
    lineas: list[LineaOperacion]
    promocion_activa: bool
    autorizada: bool
    estado: EstadoGuia = MaquinaEstadosGuia.INICIAL
    eventos: list[EventoDominio] = field(default_factory=list)

    @property
    def total(self) -> Dinero:
        """total = Σ precio_mxn × cantidad, con Decimal y 2 decimales."""
        total = Dinero.cero()
        for linea in self.lineas:
            total = total + linea.subtotal
        return total

    # --- Comandos (todos pasan por la máquina de estados) -------------------------------
    def aprobar(self) -> None:
        self._exigir_precondiciones()
        self._transicionar(E.CLASIFICADO)

    def cancelar(self) -> None:
        self._transicionar(E.CANCELADO)

    def completar(self) -> None:
        self._exigir_precondiciones()
        for destino in RUTA_COMPLETA:
            self._transicionar(destino)
        self.eventos.append(EntregaCompletada(self.operacion_id, _ahora()))

    def forzar_estado(self, destino: EstadoGuia) -> None:
        """Intento de salto directo de estado (la máquina decide si es válido)."""
        self._transicionar(destino)

    # --- Internos ------------------------------------------------------------------------
    def _exigir_precondiciones(self) -> None:
        if not (PuedeProcesarse() & ServiciosConCapacidad()).es_satisfecha_por(self):
            raise OperacionNoProcesable("; ".join(self.motivos_rechazo()))

    def motivos_rechazo(self) -> list[str]:
        motivos = []
        if not RemitenteActivo().es_satisfecha_por(self):
            motivos.append("remitente inactivo")
        if not TieneServicios().es_satisfecha_por(self):
            motivos.append("sin servicios")
        if not Autorizada().es_satisfecha_por(self):
            motivos.append("sin autorización")
        if not ServiciosConCapacidad().es_satisfecha_por(self):
            motivos.append("servicio deshabilitado o sin capacidad")
        return motivos

    def _transicionar(self, destino: EstadoGuia) -> None:
        MaquinaEstadosGuia.validar(self.estado, destino)
        self.estado = destino
        self.eventos.append(EstadoCambiado(self.operacion_id, _ahora(), destino.value))


def _ahora() -> datetime:
    return datetime.now(UTC)


# --- Specifications del paquete docente --------------------------------------------------
class RemitenteActivo(Specification):
    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return op.remitente.activo


class TieneServicios(Specification):
    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return len(op.lineas) > 0


class Autorizada(Specification):
    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return op.autorizada


class ServiciosConCapacidad(Specification):
    """Cada servicio está habilitado y la cantidad no excede su capacidad."""

    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return all(ln.servicio.habilitado and ln.cantidad <= ln.servicio.capacidad for ln in op.lineas)


class RemitentePreferente(Specification):
    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return op.remitente.preferente


class TotalAlMenos(Specification):
    def __init__(self, minimo: Dinero):
        self.minimo = minimo

    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return op.total.monto >= self.minimo.monto


class PromocionActiva(Specification):
    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return op.promocion_activa


class PuedeProcesarse(Specification):
    """puede_procesarse = remitente activo AND al menos una línea AND autorización."""

    def __init__(self):
        self._spec = RemitenteActivo() & TieneServicios() & Autorizada()

    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return self._spec.es_satisfecha_por(op)


class BeneficioReferencia(Specification):
    """beneficio_referencia = preferente AND total ≥ $1,500 AND NOT promoción activa."""

    def __init__(self, umbral: Dinero = UMBRAL_BENEFICIO):
        self._spec = RemitentePreferente() & TotalAlMenos(umbral) & ~PromocionActiva()

    def es_satisfecha_por(self, op: OperacionServicio) -> bool:
        return self._spec.es_satisfecha_por(op)
