"""US07 — docs/gherkin/US07_entrega_tercero.feature (RN-11, RN-07)."""
import pytest

from src.application.comandos import CapturarEvidenciaCommand
from src.domain.errores import EvidenciaIncompleta


def test_entrega_a_vecino(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    dto = sistema.entregas.capturar_evidencia_entrega(
        CapturarEvidenciaCommand(n, "firma.png", "foto.jpg", "Luis Pérez (vecino)", es_tercero=True))
    assert dto.estado == "ENTREGADO"
    assert sistema.guia(n).evidencia.es_tercero is True


def test_entrega_a_tercero_sin_nombre(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    with pytest.raises(EvidenciaIncompleta):
        sistema.entregas.capturar_evidencia_entrega(
            CapturarEvidenciaCommand(n, "firma.png", "foto.jpg", "", es_tercero=True))
