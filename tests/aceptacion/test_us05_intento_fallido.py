"""US05 — docs/gherkin/US05_intento_fallido.feature (RN-06)."""
import pytest

from src.domain.errores import LimiteIntentosExcedido, TransicionEstadoInvalida


@pytest.fixture
def en_reparto(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    return n


def test_primer_intento_fallido(sistema, en_reparto):
    dto = sistema.entregas.registrar_intento_fallido(en_reparto, "destinatario ausente")
    assert dto.intentos_fallidos == 1
    assert dto.estado == "EN_REPARTO"


def test_segundo_intento_fallido_envia_a_resguardo(sistema, en_reparto):
    sistema.entregas.registrar_intento_fallido(en_reparto, "ausente")
    dto = sistema.entregas.registrar_intento_fallido(en_reparto, "ausente")
    assert dto.estado == "EN_RESGUARDO"
    assert "GuiaEnResguardo" in sistema.publicador.tipos()  # notificación al destinatario


def test_tercer_intento_es_rechazado(sistema, en_reparto):
    for _ in range(2):
        sistema.entregas.registrar_intento_fallido(en_reparto, "ausente")
    with pytest.raises(LimiteIntentosExcedido):
        sistema.entregas.registrar_intento_fallido(en_reparto, "ausente")


def test_intento_fuera_de_reparto(sistema):
    n = sistema.registrar().numero
    with pytest.raises(TransicionEstadoInvalida):
        sistema.entregas.registrar_intento_fallido(n, "ausente")
