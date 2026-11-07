"""US02 — docs/gherkin/US02_cancelacion_temprana.feature (RN-09)."""
import pytest

from src.domain.errores import CancelacionNoPermitida


def test_cancelar_guia_en_recibido(sistema):
    n = sistema.registrar().numero
    assert sistema.envios.cancelar(n).estado == "CANCELADO"
    assert sistema.guia(n).eventos[-1].estado.value == "CANCELADO"


def test_no_se_cancela_una_guia_clasificada(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "CLASIFICADO")
    with pytest.raises(CancelacionNoPermitida):
        sistema.envios.cancelar(n)
    assert sistema.guia(n).estado.value == "CLASIFICADO"
