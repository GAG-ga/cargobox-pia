from decimal import Decimal

import pytest

from src.domain.errores import DatoInvalido, EvidenciaIncompleta
from src.domain.value_objects import (
    Dimensiones,
    Dinero,
    Direccion,
    EvidenciaEntrega,
    NumeroGuia,
    Paquete,
    Persona,
    Peso,
    Zona,
)


def test_numero_guia_valido_y_desde_secuencia():
    assert NumeroGuia.desde_secuencia(7) == NumeroGuia("CBX-000007")
    assert str(NumeroGuia("CBX-000001")) == "CBX-000001"


@pytest.mark.parametrize("valor", ["123", "CBX-1", "cbx-000001", ""])
def test_numero_guia_invalido(valor):
    with pytest.raises(DatoInvalido):
        NumeroGuia(valor)


def test_dinero_redondea_a_centavos_y_opera():
    assert Dinero(Decimal("10.005")).monto == Decimal("10.01")
    assert (Dinero(Decimal("5")) + Dinero(Decimal("2.5"))).monto == Decimal("7.50")
    assert Dinero(Decimal("400")).por(Decimal("0.5")).monto == Decimal("200.00")
    assert Dinero(Decimal("8000")).minimo(Dinero(Decimal("5000"))).monto == Decimal("5000.00")
    assert Dinero(Decimal("1200")).minimo(Dinero(Decimal("5000"))).monto == Decimal("1200.00")


def test_dinero_negativo_es_invalido():
    with pytest.raises(DatoInvalido):
        Dinero(Decimal("-1"))


@pytest.mark.parametrize("kg", [0, -1])
def test_peso_debe_ser_positivo(kg):
    with pytest.raises(DatoInvalido):
        Peso(kg)


def test_dimensiones_y_peso_volumetrico():
    d = Dimensiones(50, 40, 30)
    assert d.peso_volumetrico == Decimal("12")
    assert d.lado_mayor == 50
    with pytest.raises(DatoInvalido):
        Dimensiones(0, 10, 10)


def test_kg_cobrable_es_el_mayor_entre_real_y_volumetrico():
    assert Paquete(Peso(2), Dimensiones(50, 40, 30)).kg_cobrable == 12  # volumétrico
    assert Paquete(Peso(10), Dimensiones(40, 30, 20)).kg_cobrable == 10  # real


@pytest.mark.parametrize("nombre, telefono", [("", "8112345678"), ("Ana", "123")])
def test_persona_invalida(nombre, telefono):
    with pytest.raises(DatoInvalido):
        Persona(nombre, telefono)


@pytest.mark.parametrize("calle, cp", [("", "66450"), ("Roble 10", "664")])
def test_direccion_invalida(calle, cp):
    with pytest.raises(DatoInvalido):
        Direccion(calle, cp)


@pytest.mark.parametrize("cp_destino, zona", [("66220", Zona.LOCAL), ("64000", Zona.REGIONAL),
                                              ("01000", Zona.NACIONAL)])
def test_zona_por_codigo_postal(cp_destino, zona):
    assert Zona.entre(Direccion("A", "66450"), Direccion("B", cp_destino)) == zona


@pytest.mark.parametrize("firma, foto, nombre", [("", "f.jpg", "Ana"), ("f.png", "", "Ana"),
                                                 ("f.png", "f.jpg", "  ")])
def test_evidencia_incompleta(firma, foto, nombre):
    with pytest.raises(EvidenciaIncompleta):
        EvidenciaEntrega(firma, foto, nombre)
