from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from src.domain.especificaciones import (
    CumpleLimitesEstandar,
    EnEstado,
    EnSeguimientoActivo,
    ExpressFueraDeTiempo,
    PuedeDeclararsePerdida,
    RequiereAlertaPorRetraso,
    ResguardoVencido,
)
from src.domain.estados import EstadoGuia as E
from src.domain.value_objects import Dimensiones, NivelServicio, Paquete, Peso

AHORA = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)


@dataclass
class GuiaFalsa:
    estado: E
    ultima_actualizacion: datetime = AHORA
    nivel: NivelServicio = NivelServicio.ESTANDAR
    con_garantia: bool = True
    creada_en: datetime = AHORA
    resguardo_desde: datetime | None = None


def test_combinadores_y_o_no():
    reparto, transito = EnEstado(E.EN_REPARTO), EnEstado(E.EN_TRANSITO)
    g = GuiaFalsa(E.EN_REPARTO)
    assert (reparto | transito).es_satisfecha_por(g)
    assert not (reparto & transito).es_satisfecha_por(g)
    assert (~transito).es_satisfecha_por(g)


@pytest.mark.parametrize("peso, dims, esperado", [
    (30, (100, 100, 100), True), (30.01, (40, 30, 20), False), (10, (101, 50, 50), False)])
def test_cumple_limites_estandar(peso, dims, esperado):
    assert CumpleLimitesEstandar().es_satisfecha_por(Paquete(Peso(peso), Dimensiones(*dims))) is esperado


def test_seguimiento_activo_excluye_finales_y_resguardo():
    assert EnSeguimientoActivo().es_satisfecha_por(GuiaFalsa(E.EN_TRANSITO))
    assert not EnSeguimientoActivo().es_satisfecha_por(GuiaFalsa(E.EN_RESGUARDO))
    assert not EnSeguimientoActivo().es_satisfecha_por(GuiaFalsa(E.ENTREGADO))


@pytest.mark.parametrize("horas, esperado", [(24, True), (23, False)])
def test_alerta_por_retraso_24h(horas, esperado):
    g = GuiaFalsa(E.EN_TRANSITO, AHORA - timedelta(hours=horas))
    assert RequiereAlertaPorRetraso(AHORA).es_satisfecha_por(g) is esperado


@pytest.mark.parametrize("dias, estado, esperado", [
    (11, E.EN_TRANSITO, True), (10, E.EN_TRANSITO, False), (11, E.RECIBIDO, False)])
def test_puede_declararse_perdida(dias, estado, esperado):
    g = GuiaFalsa(estado, AHORA - timedelta(days=dias))
    assert PuedeDeclararsePerdida(AHORA).es_satisfecha_por(g) is esperado


def test_resguardo_vencido_cuenta_dias_habiles():
    desde = datetime(2026, 11, 2, 9, tzinfo=UTC)  # lunes
    g = GuiaFalsa(E.EN_RESGUARDO, resguardo_desde=desde)
    assert not ResguardoVencido(datetime(2026, 11, 9, 9, tzinfo=UTC)).es_satisfecha_por(g)
    assert ResguardoVencido(datetime(2026, 11, 10, 9, tzinfo=UTC)).es_satisfecha_por(g)


def test_express_fuera_de_tiempo():
    g = GuiaFalsa(E.EN_REPARTO, nivel=NivelServicio.EXPRESS, creada_en=AHORA - timedelta(hours=49))
    assert ExpressFueraDeTiempo(AHORA).es_satisfecha_por(g)
    g.con_garantia = False
    assert not ExpressFueraDeTiempo(AHORA).es_satisfecha_por(g)
