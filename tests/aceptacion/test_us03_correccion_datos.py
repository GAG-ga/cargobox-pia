"""US03 — docs/gherkin/US03_correccion_datos.feature (RN-10)."""
import pytest

from src.domain.errores import CorreccionNoPermitida


def test_corregir_destino_sin_nueva_guia(sistema):
    n = sistema.registrar().numero
    dto = sistema.envios.corregir_datos(n, destino=("Calle Roble 12", "66220"))
    assert dto.numero == n
    assert dto.destino == "Calle Roble 12, CP 66220"
    assert len(sistema.uow.guias.datos) == 1


def test_no_se_corrigen_datos_de_guia_clasificada(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "CLASIFICADO")
    with pytest.raises(CorreccionNoPermitida):
        sistema.envios.corregir_datos(n, destino=("Calle Roble 12", "66220"))
