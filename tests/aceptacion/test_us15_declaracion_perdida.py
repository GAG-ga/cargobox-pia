"""US15 — docs/gherkin/US15_declaracion_perdida.feature (RN-18)."""
from decimal import Decimal

import pytest

from src.domain.errores import PerdidaNoDeclarable


def guia_en_transito(sistema, valor):
    n = sistema.registrar(valor_declarado=Decimal(valor)).numero
    sistema.avanzar_hasta(n, "EN_TRANSITO")
    return n


def test_perdida_con_compensacion_igual_al_valor_declarado(sistema):
    n = guia_en_transito(sistema, "1200")
    sistema.reloj.avanzar(days=11)
    dto = sistema.incidencias.declarar_perdida(n)
    assert (dto.estado, dto.compensacion) == ("PERDIDO", "1200.00")
    assert "PerdidaDeclarada" in sistema.publicador.tipos()


def test_compensacion_respeta_tope_de_5000(sistema):
    n = guia_en_transito(sistema, "8000")
    sistema.reloj.avanzar(days=11)
    assert sistema.incidencias.declarar_perdida(n).compensacion == "5000.00"


def test_con_10_dias_exactos_no_se_declara(sistema):
    n = guia_en_transito(sistema, "1200")
    sistema.reloj.avanzar(days=10)
    with pytest.raises(PerdidaNoDeclarable):
        sistema.incidencias.declarar_perdida(n)
