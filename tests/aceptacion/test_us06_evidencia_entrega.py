"""US06 — docs/gherkin/US06_evidencia_entrega.feature (RN-07, RN-19)."""
from decimal import Decimal

import pytest

from src.application.comandos import CapturarEvidenciaCommand
from src.domain.errores import EntregaYaRegistrada, EvidenciaIncompleta


def entregar(sistema, n, foto="foto.jpg"):
    return sistema.entregas.capturar_evidencia_entrega(
        CapturarEvidenciaCommand(n, "firma.png", foto, "Ana López"))


def test_entrega_con_firma_y_foto(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    dto = entregar(sistema, n)
    assert dto.estado == "ENTREGADO"
    assert sistema.guia(n).evidencia.foto == "foto.jpg"
    sistema.almacen.guardar.assert_called_once_with(n, "firma.png", "foto.jpg")
    assert dto.reembolso == "0.00"


def test_entrega_sin_foto_no_se_permite(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    with pytest.raises(EvidenciaIncompleta):
        entregar(sistema, n, foto="")
    assert sistema.guia(n).estado.value == "EN_REPARTO"
    sistema.almacen.guardar.assert_not_called()


def test_express_entregado_tarde_genera_reembolso_50(sistema):
    n = sistema.registrar(nivel="EXPRESS", peso_kg=Decimal("1"), largo_cm=10, ancho_cm=10,
                          alto_cm=10, destino_cp="01000").numero
    tarifa = Decimal(sistema.guia(n).tarifa.monto)
    sistema.avanzar_hasta(n, "EN_REPARTO")
    sistema.reloj.avanzar(hours=60)
    dto = entregar(sistema, n)
    assert Decimal(dto.reembolso) == (tarifa / 2).quantize(Decimal("0.01"))


def test_segunda_entrega_rechazada(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    entregar(sistema, n)
    with pytest.raises(EntregaYaRegistrada):
        entregar(sistema, n)
