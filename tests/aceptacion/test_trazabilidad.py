"""Trazabilidad: cada historia en Gherkin tiene su módulo de pruebas y al menos tantas pruebas
como escenarios."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def test_cada_feature_tiene_pruebas_de_aceptacion():
    for feature in sorted((RAIZ / "docs/gherkin").glob("US*.feature")):
        us = feature.name[:4].lower()
        modulos = list((RAIZ / "tests/aceptacion").glob(f"test_{us}_*.py"))
        assert modulos, f"{feature.name} no tiene pruebas"
        escenarios = len(re.findall(r"^\s*(Escenario|Esquema del escenario):", feature.read_text(
            encoding="utf-8"), re.M))
        pruebas = len(re.findall(r"^def test_", modulos[0].read_text(encoding="utf-8"), re.M))
        assert pruebas >= escenarios, f"{feature.name}: {escenarios} escenarios, {pruebas} pruebas"
