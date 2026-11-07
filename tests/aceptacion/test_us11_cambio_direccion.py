"""US11 — docs/gherkin/US11_cambio_direccion.feature (RN-14)."""
import pytest

from src.application.comandos import CambiarDireccionCommand
from src.domain.errores import CambioDireccionNoPermitido, IdentidadNoValidada


def cmd(n, validada=True):
    return CambiarDireccionCommand(n, "Av. Reforma 500", "06600", validada)


def test_cambio_con_identidad_validada(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_TRANSITO")
    dto = sistema.envios.cambiar_direccion(cmd(n))
    assert dto.destino == "Av. Reforma 500, CP 06600"
    assert dto.cargos_adicionales == "80.00"
    assert dto.con_garantia is False


def test_sin_validacion_de_identidad(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_TRANSITO")
    with pytest.raises(IdentidadNoValidada):
        sistema.envios.cambiar_direccion(cmd(n, validada=False))


def test_no_se_cambia_en_reparto(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    with pytest.raises(CambioDireccionNoPermitido):
        sistema.envios.cambiar_direccion(cmd(n))
