"""US14 — docs/gherkin/US14_paquete_danado.feature (RN-17)."""
import pytest

from src.application.errores import IncidenciaNoEncontrada
from src.domain.errores import EvidenciaIncompleta


def test_folio_con_evidencia_se_asigna_al_supervisor_de_origen(sistema):
    n = sistema.registrar().numero
    dto = sistema.incidencias.abrir_folio_dano(n, "dano.jpg")
    assert dto.folio.startswith("INC-")
    assert dto.tipo == "DANO"
    assert dto.asignada_a == "Supervisor de Sucursal San Nicolás"


def test_folio_sin_foto_no_se_registra(sistema):
    n = sistema.registrar().numero
    with pytest.raises(EvidenciaIncompleta):
        sistema.incidencias.abrir_folio_dano(n, "")


def test_supervisor_resuelve_con_reembolso(sistema):
    n = sistema.registrar().numero
    folio = sistema.incidencias.abrir_folio_dano(n, "dano.jpg").folio
    dto = sistema.incidencias.resolver(folio, "REEMBOLSO")
    assert (dto.estado, dto.resolucion) == ("RESUELTA", "REEMBOLSO")


def test_resolver_folio_inexistente(sistema):
    with pytest.raises(IncidenciaNoEncontrada):
        sistema.incidencias.resolver("INC-999999", "REEMBOLSO")
