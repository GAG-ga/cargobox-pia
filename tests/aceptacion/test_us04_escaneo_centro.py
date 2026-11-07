"""US04 — docs/gherkin/US04_escaneo_centro.feature (RN-04, RN-05)."""
import pytest

from src.application.comandos import RegistrarEscaneoCommand
from src.application.errores import GuiaNoEncontrada
from src.domain.errores import TransicionEstadoInvalida


def test_escaneo_avanza_estado_y_registra_evento(sistema):
    n = sistema.registrar().numero
    sistema.reloj.avanzar(hours=3)
    dto = sistema.rastreo.registrar_escaneo(RegistrarEscaneoCommand(n, "CLASIFICADO", "CEDIS Monterrey"))
    assert dto.estado == "CLASIFICADO"
    evento = sistema.guia(n).eventos[-1]
    assert (evento.ubicacion, evento.fecha_hora) == ("CEDIS Monterrey", sistema.reloj.ahora())


def test_escaneo_que_salta_estado_es_rechazado(sistema):
    n = sistema.registrar().numero
    with pytest.raises(TransicionEstadoInvalida):
        sistema.rastreo.registrar_escaneo(RegistrarEscaneoCommand(n, "EN_TRANSITO", "CEDIS"))
    assert len(sistema.guia(n).eventos) == 1


def test_escaneo_no_puede_marcar_entregado(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    with pytest.raises(TransicionEstadoInvalida):
        sistema.rastreo.registrar_escaneo(RegistrarEscaneoCommand(n, "ENTREGADO", "Domicilio"))


def test_escaneo_de_guia_inexistente(sistema):
    with pytest.raises(GuiaNoEncontrada):
        sistema.rastreo.registrar_escaneo(RegistrarEscaneoCommand("CBX-999999", "CLASIFICADO", "X"))
