"""US08 — docs/gherkin/US08_consulta_destinatario.feature (RN-12, RN-20)."""
import pytest

from src.application.errores import GuiaNoEncontrada


def test_consulta_publica_solo_estado_y_fecha(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_TRANSITO")
    vista = sistema.consultas.estado_publico(n)
    assert vista["estado"] == "EN_TRANSITO"
    assert vista["fecha_estimada"] is not None
    assert vista["mensaje"] == "Tu paquete va en camino hacia la ciudad de destino."
    assert "eventos" not in vista and "telefono_remitente" not in vista


def test_guia_inexistente(sistema):
    with pytest.raises(GuiaNoEncontrada) as error:
        sistema.consultas.estado_publico("CBX-999999")
    assert "No encontramos" in error.value.mensaje
