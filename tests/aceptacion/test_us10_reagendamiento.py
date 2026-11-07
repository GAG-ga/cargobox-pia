"""US10 — docs/gherkin/US10_reagendamiento.feature (RN-13)."""
from datetime import UTC, datetime

import pytest

from src.application.comandos import CapturarEvidenciaCommand
from src.domain.errores import ReagendamientoNoPermitido

LUNES_2 = datetime(2026, 11, 2, 9, tzinfo=UTC)


@pytest.fixture
def en_resguardo(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    for _ in range(2):
        sistema.entregas.registrar_intento_fallido(n, "ausente")
    assert sistema.guia(n).resguardo_desde == LUNES_2
    return n


def test_reagendar_dentro_del_plazo(sistema, en_resguardo):
    sistema.reloj.fijar(datetime(2026, 11, 4, 9, tzinfo=UTC))
    assert sistema.entregas.reagendar(en_resguardo).estado == "EN_REPARTO"


def test_recoger_en_centro_dentro_del_plazo(sistema, en_resguardo):
    dto = sistema.entregas.capturar_evidencia_entrega(CapturarEvidenciaCommand(
        en_resguardo, "firma.png", "foto.jpg", "Ana López", ubicacion="CEDIS CDMX"))
    assert dto.estado == "ENTREGADO"


def test_vence_el_resguardo_sin_accion(sistema, en_resguardo):
    sistema.reloj.fijar(datetime(2026, 11, 10, 9, tzinfo=UTC))
    assert sistema.incidencias.vencer_resguardos() == [en_resguardo]
    assert sistema.guia(en_resguardo).estado.value == "DEVUELTO"


def test_dia_5_habil_sigue_en_plazo(sistema, en_resguardo):
    sistema.reloj.fijar(datetime(2026, 11, 9, 9, tzinfo=UTC))
    assert sistema.incidencias.vencer_resguardos() == []
    assert sistema.guia(en_resguardo).estado.value == "EN_RESGUARDO"


def test_solo_un_reagendamiento(sistema, en_resguardo):
    sistema.entregas.reagendar(en_resguardo)
    sistema.entregas.registrar_intento_fallido(en_resguardo, "ausente otra vez")
    assert sistema.guia(en_resguardo).estado.value == "EN_RESGUARDO"
    with pytest.raises(ReagendamientoNoPermitido):
        sistema.entregas.reagendar(en_resguardo)


def test_no_se_reagenda_con_plazo_vencido(sistema, en_resguardo):
    sistema.reloj.fijar(datetime(2026, 11, 10, 9, tzinfo=UTC))
    with pytest.raises(ReagendamientoNoPermitido):
        sistema.entregas.reagendar(en_resguardo)
