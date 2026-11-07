"""RN-03: cotización. Domain Service + Strategy (una política por nivel de servicio)."""
from decimal import Decimal

from src.domain.value_objects import Dinero, Direccion, NivelServicio, Paquete, Zona

TARIFA_BASE = Decimal("99")
POR_KG = Decimal("15")
FACTOR_ZONA = {Zona.LOCAL: Decimal("1.0"), Zona.REGIONAL: Decimal("1.3"),
               Zona.NACIONAL: Decimal("1.6")}


class PoliticaTarifa:
    nivel: NivelServicio
    factor: Decimal


class TarifaEstandar(PoliticaTarifa):
    nivel = NivelServicio.ESTANDAR
    factor = Decimal("1.0")


class TarifaExpress(PoliticaTarifa):
    nivel = NivelServicio.EXPRESS
    factor = Decimal("1.8")


class Cotizador:
    def __init__(self, politicas: list[PoliticaTarifa] | None = None):
        politicas = politicas or [TarifaEstandar(), TarifaExpress()]
        self._politicas = {p.nivel: p for p in politicas}

    def cotizar(self, paquete: Paquete, origen: Direccion, destino: Direccion,
                nivel: NivelServicio) -> Dinero:
        base = TARIFA_BASE + POR_KG * paquete.kg_cobrable
        zona = Zona.entre(origen, destino)
        return Dinero(base * FACTOR_ZONA[zona] * self._politicas[nivel].factor)
