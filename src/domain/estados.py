"""State Machine del ciclo de vida de la guía (ADR-007, BRD §9.1)."""
from enum import StrEnum

from src.domain.errores import TransicionEstadoInvalida


class EstadoGuia(StrEnum):
    RECIBIDO = "RECIBIDO"
    CLASIFICADO = "CLASIFICADO"
    EN_TRANSITO = "EN_TRANSITO"
    CENTRO_DESTINO = "CENTRO_DESTINO"
    EN_REPARTO = "EN_REPARTO"
    ENTREGADO = "ENTREGADO"
    EN_RESGUARDO = "EN_RESGUARDO"
    DEVUELTO = "DEVUELTO"
    CANCELADO = "CANCELADO"
    PERDIDO = "PERDIDO"


E = EstadoGuia


class MaquinaEstadosGuia:
    """Tabla de transiciones permitidas: {origen: {destino: acción}}."""

    TRANSICIONES: dict[EstadoGuia, dict[EstadoGuia, str]] = {
        E.RECIBIDO: {E.CLASIFICADO: "escaneo de ingreso", E.CANCELADO: "cancelar"},
        E.CLASIFICADO: {E.EN_TRANSITO: "escaneo de salida"},
        E.EN_TRANSITO: {E.CENTRO_DESTINO: "escaneo en destino", E.PERDIDO: "declarar pérdida"},
        E.CENTRO_DESTINO: {E.EN_REPARTO: "salida a ruta", E.PERDIDO: "declarar pérdida"},
        E.EN_REPARTO: {
            E.ENTREGADO: "entrega con evidencia",
            E.EN_RESGUARDO: "intento fallido",
            E.PERDIDO: "declarar pérdida",
        },
        E.EN_RESGUARDO: {
            E.EN_REPARTO: "reagendar",
            E.ENTREGADO: "recoger en centro",
            E.DEVUELTO: "vencimiento del resguardo",
        },
        E.ENTREGADO: {},
        E.DEVUELTO: {},
        E.CANCELADO: {},
        E.PERDIDO: {},
    }
    INICIAL = E.RECIBIDO

    @classmethod
    def puede(cls, origen: EstadoGuia, destino: EstadoGuia) -> bool:
        return destino in cls.TRANSICIONES[origen]

    @classmethod
    def validar(cls, origen: EstadoGuia, destino: EstadoGuia) -> str:
        if not cls.puede(origen, destino):
            raise TransicionEstadoInvalida(f"{origen.value} → {destino.value} no está permitido")
        return cls.TRANSICIONES[origen][destino]

    @classmethod
    def es_final(cls, estado: EstadoGuia) -> bool:
        return not cls.TRANSICIONES[estado]
