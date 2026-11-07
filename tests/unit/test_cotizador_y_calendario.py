from datetime import date
from decimal import Decimal

from src.domain.calendario import dias_habiles_transcurridos, sumar_dias_habiles
from src.domain.cotizador import Cotizador
from src.domain.value_objects import Dimensiones, Direccion, NivelServicio, Paquete, Peso

ORIGEN = Direccion("Av. Universidad 100", "66450")


def test_tarifa_estandar_local():
    p = Paquete(Peso(10), Dimensiones(40, 30, 20))
    tarifa = Cotizador().cotizar(p, ORIGEN, Direccion("Roble 10", "66220"), NivelServicio.ESTANDAR)
    assert tarifa.monto == Decimal("249.00")  # 99 + 15*10


def test_tarifa_express_nacional_con_peso_volumetrico():
    p = Paquete(Peso(2), Dimensiones(50, 40, 30))
    tarifa = Cotizador().cotizar(p, ORIGEN, Direccion("Centro 1", "01000"), NivelServicio.EXPRESS)
    assert tarifa.monto == Decimal("803.52")  # (99 + 15*12) * 1.6 * 1.8


def test_tarifa_regional():
    p = Paquete(Peso(1), Dimensiones(10, 10, 10))
    tarifa = Cotizador().cotizar(p, ORIGEN, Direccion("Centro 1", "64000"), NivelServicio.ESTANDAR)
    assert tarifa.monto == Decimal("148.20")  # (99 + 15) * 1.3


def test_dias_habiles():
    lunes = date(2026, 11, 2)
    assert sumar_dias_habiles(lunes, 5) == date(2026, 11, 9)
    assert sumar_dias_habiles(date(2026, 11, 6), 1) == date(2026, 11, 9)  # viernes → lunes
    assert dias_habiles_transcurridos(lunes, date(2026, 11, 9)) == 5
    assert dias_habiles_transcurridos(lunes, date(2026, 11, 10)) == 6
