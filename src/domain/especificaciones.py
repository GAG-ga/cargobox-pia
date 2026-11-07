"""Patrón Specification (ADR-006): cada condición del negocio es una clase con nombre propio."""
from datetime import datetime, timedelta

from src.domain.calendario import dias_habiles_transcurridos
from src.domain.estados import EstadoGuia, MaquinaEstadosGuia
from src.domain.incidencia import EstadoIncidencia, TipoIncidencia
from src.domain.value_objects import LADO_MAXIMO_CM, PESO_MAXIMO_KG, NivelServicio

E = EstadoGuia


class Specification:
    def es_satisfecha_por(self, candidato) -> bool:  # pragma: no cover - abstracto
        raise NotImplementedError

    def __and__(self, otra: "Specification") -> "Specification":
        return _Y(self, otra)

    def __or__(self, otra: "Specification") -> "Specification":
        return _O(self, otra)

    def __invert__(self) -> "Specification":
        return _No(self)


class _Y(Specification):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def es_satisfecha_por(self, c):
        return self.a.es_satisfecha_por(c) and self.b.es_satisfecha_por(c)


class _O(Specification):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def es_satisfecha_por(self, c):
        return self.a.es_satisfecha_por(c) or self.b.es_satisfecha_por(c)


class _No(Specification):
    def __init__(self, a):
        self.a = a

    def es_satisfecha_por(self, c):
        return not self.a.es_satisfecha_por(c)


class EnEstado(Specification):
    def __init__(self, *estados: EstadoGuia):
        self.estados = set(estados)

    def es_satisfecha_por(self, guia):
        return guia.estado in self.estados


# ---------- RN-01 ----------
class CumpleLimitesEstandar(Specification):
    """Peso ≤ 30 kg y cada lado ≤ 100 cm. Candidato: Paquete."""

    def es_satisfecha_por(self, paquete):
        return (paquete.peso.kg <= PESO_MAXIMO_KG
                and paquete.dimensiones.lado_mayor <= LADO_MAXIMO_CM)


# ---------- RN-09 / RN-10 / RN-14 ----------
class PuedeCancelarse(EnEstado):
    def __init__(self):
        super().__init__(E.RECIBIDO)


class PermiteCorreccion(EnEstado):
    def __init__(self):
        super().__init__(E.RECIBIDO)


class PermiteCambioDireccion(EnEstado):
    def __init__(self):
        super().__init__(E.EN_TRANSITO, E.CENTRO_DESTINO)


# ---------- reglas de tiempo (reciben `ahora`) ----------
class SinActualizacionDesde(Specification):
    def __init__(self, ahora: datetime, limite: timedelta, estricto: bool = False):
        self.ahora, self.limite, self.estricto = ahora, limite, estricto

    def es_satisfecha_por(self, guia):
        transcurrido = self.ahora - guia.ultima_actualizacion
        return transcurrido > self.limite if self.estricto else transcurrido >= self.limite


ESTADOS_EN_SEGUIMIENTO = frozenset(
    e for e in EstadoGuia if not MaquinaEstadosGuia.es_final(e) and e != E.EN_RESGUARDO)


class EnSeguimientoActivo(EnEstado):
    """Guía viva que debería moverse: no está en un estado final ni en resguardo."""

    def __init__(self):
        super().__init__(*ESTADOS_EN_SEGUIMIENTO)


class RequiereAlertaPorRetraso(Specification):
    """RN-15: 24 h o más sin cambio de estado."""

    def __init__(self, ahora: datetime):
        self._spec = EnSeguimientoActivo() & SinActualizacionDesde(ahora, timedelta(hours=24))

    def es_satisfecha_por(self, guia):
        return self._spec.es_satisfecha_por(guia)


class PuedeDeclararsePerdida(Specification):
    """RN-18: en ruta y más de 10 días naturales sin actualización."""

    def __init__(self, ahora: datetime):
        self._spec = (EnEstado(E.EN_TRANSITO, E.CENTRO_DESTINO, E.EN_REPARTO)
                      & SinActualizacionDesde(ahora, timedelta(days=10), estricto=True))

    def es_satisfecha_por(self, guia):
        return self._spec.es_satisfecha_por(guia)


class ResguardoVencido(Specification):
    """RN-13: más de 5 días hábiles en resguardo."""

    def __init__(self, ahora: datetime):
        self.ahora = ahora

    def es_satisfecha_por(self, guia):
        return (guia.estado == E.EN_RESGUARDO and guia.resguardo_desde is not None
                and dias_habiles_transcurridos(guia.resguardo_desde.date(), self.ahora.date()) > 5)


class ExpressFueraDeTiempo(Specification):
    """RN-19: Express con garantía entregado después de 48 h."""

    def __init__(self, ahora: datetime):
        self.ahora = ahora

    def es_satisfecha_por(self, guia):
        return (guia.nivel == NivelServicio.EXPRESS and guia.con_garantia
                and self.ahora - guia.creada_en > timedelta(hours=48))


class DebeEscalarse(Specification):
    """RN-16: alerta abierta con 48 h o más. Candidato: Incidencia."""

    def __init__(self, ahora: datetime):
        self.ahora = ahora

    def es_satisfecha_por(self, incidencia):
        return (incidencia.tipo == TipoIncidencia.RETRASO
                and incidencia.estado == EstadoIncidencia.ABIERTA
                and self.ahora - incidencia.abierta_en >= timedelta(hours=48))
