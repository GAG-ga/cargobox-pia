"""US01 — docs/gherkin/US01_registro_guia.feature (RN-01, RN-02, RN-03, RN-20)."""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.errores import CargaEspecialRequerida


def test_paquete_dentro_de_limites_genera_guia_estandar(sistema):
    dto = sistema.registrar()
    assert dto.numero == "CBX-000001"
    assert dto.estado == "RECIBIDO"
    assert dto.tarifa == "249.00"
    assert dto.fecha_estimada == date(2026, 11, 9)  # lunes 2 + 5 días hábiles
    assert "GuiaGenerada" in sistema.publicador.tipos()
    assert len(sistema.guia("CBX-000001").eventos) == 1


@pytest.mark.parametrize("peso, medidas", [("30.01", (40, 30, 20)), ("10", (101, 50, 50))])
def test_paquete_que_excede_limites_es_carga_especial(sistema, peso, medidas):
    with pytest.raises(CargaEspecialRequerida):
        sistema.registrar(peso_kg=Decimal(peso), largo_cm=medidas[0], ancho_cm=medidas[1],
                          alto_cm=medidas[2])
    assert sistema.uow.guias.datos == {}
    assert sistema.uow.rollbacks == 1


def test_paquete_exactamente_en_el_limite_se_acepta(sistema):
    dto = sistema.registrar(peso_kg=Decimal("30"), largo_cm=100, ancho_cm=100, alto_cm=100)
    assert dto.estado == "RECIBIDO"


def test_tarifa_express_nacional_con_peso_volumetrico(sistema):
    dto = sistema.registrar(peso_kg=Decimal("2"), largo_cm=50, ancho_cm=40, alto_cm=30,
                            destino_cp="01000", nivel="EXPRESS")
    assert dto.tarifa == "803.52"
    assert dto.fecha_estimada == date(2026, 11, 4)  # 48 h


def test_numeros_de_guia_son_unicos(sistema):
    assert sistema.registrar().numero != sistema.registrar().numero
