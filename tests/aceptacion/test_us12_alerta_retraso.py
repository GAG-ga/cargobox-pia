"""US12 — docs/gherkin/US12_alerta_retraso.feature (RN-15)."""
from src.application.comandos import CapturarEvidenciaCommand


def guia_en_transito(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_TRANSITO")
    return n


def test_24_horas_sin_cambio_genera_alerta(sistema):
    n = guia_en_transito(sistema)
    sistema.reloj.avanzar(hours=24)
    folios = sistema.incidencias.monitorear_retrasos()
    assert len(folios) == 1
    assert sistema.uow.incidencias.por_folio(folios[0]).numero_guia == n
    assert "AlertaGenerada" in sistema.publicador.tipos()


def test_23_horas_no_genera_alerta(sistema):
    guia_en_transito(sistema)
    sistema.reloj.avanzar(hours=23)
    assert sistema.incidencias.monitorear_retrasos() == []


def test_guia_entregada_no_genera_alerta(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    sistema.entregas.capturar_evidencia_entrega(
        CapturarEvidenciaCommand(n, "f.png", "f.jpg", "Ana López"))
    sistema.reloj.avanzar(hours=72)
    assert sistema.incidencias.monitorear_retrasos() == []


def test_no_se_duplica_la_alerta(sistema):
    guia_en_transito(sistema)
    sistema.reloj.avanzar(hours=30)
    sistema.incidencias.monitorear_retrasos()
    sistema.reloj.avanzar(hours=1)
    assert sistema.incidencias.monitorear_retrasos() == []
    assert len(sistema.uow.incidencias.abiertas()) == 1
