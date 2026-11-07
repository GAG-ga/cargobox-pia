"""US09 — docs/gherkin/US09_historial_remitente.feature (RN-08, RN-05)."""
import pytest

from src.application.errores import AccesoDenegado, GuiaNoEncontrada


def test_remitente_ve_todos_los_eventos_en_orden(sistema):
    n = sistema.registrar().numero
    sistema.reloj.avanzar(hours=1)
    sistema.avanzar_hasta(n, "EN_TRANSITO")
    vista = sistema.consultas.historial(n, "8112345678")
    assert [e["estado"] for e in vista["eventos"]] == ["RECIBIDO", "CLASIFICADO", "EN_TRANSITO"]
    fechas = [e["fecha_hora"] for e in vista["eventos"]]
    assert fechas == sorted(fechas)


def test_historial_de_guia_inexistente(sistema):
    with pytest.raises(GuiaNoEncontrada):
        sistema.consultas.historial("CBX-999999", "8112345678")


def test_otra_persona_no_puede_ver_el_historial(sistema):
    n = sistema.registrar().numero
    with pytest.raises(AccesoDenegado):
        sistema.consultas.historial(n, "8100000000")
