import os

import pytest
from fastapi.testclient import TestClient

from src.api.main import crear_app
from src.infrastructure.config import Configuracion
from src.infrastructure.db import crear_engine
from src.infrastructure.modelos import Base


def url_de_pruebas() -> str:
    """SQLite en memoria por defecto; PostgreSQL si existe TEST_DATABASE_URL (Docker y CI)."""
    return os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


def base_limpia(url: str) -> str:
    """Cada prueba empieza con las tablas vacías."""
    if not url.startswith("sqlite"):
        engine = crear_engine(url)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        engine.dispose()
    return url

GUIA = {
    "remitente": {"nombre": "Carlos Ruiz", "telefono": "8112345678"},
    "destinatario": {"nombre": "Ana López", "telefono": "8187654321"},
    "origen": {"calle": "Av. Universidad 100", "codigo_postal": "66450"},
    "destino": {"calle": "Calle Roble 10", "codigo_postal": "66220"},
    "paquete": {"peso_kg": 10, "largo_cm": 40, "ancho_cm": 30, "alto_cm": 20},
    "nivel": "ESTANDAR",
    "valor_declarado": 1200,
    "sucursal": "Sucursal San Nicolás",
}
RUTA = [("CLASIFICADO", "CEDIS Monterrey"), ("EN_TRANSITO", "Ruta MTY-CDMX"),
        ("CENTRO_DESTINO", "CEDIS CDMX"), ("EN_REPARTO", "Unidad 12")]


@pytest.fixture
def cliente(tmp_path):
    """API completa contra la base de pruebas (vacía al iniciar cada prueba)."""
    url = base_limpia(url_de_pruebas())
    app = crear_app(Configuracion(url, "test", str(tmp_path / "evidencias")))
    with TestClient(app) as c:
        yield c
    app.state.contenedor.engine.dispose()


@pytest.fixture
def nueva_guia(cliente):
    def crear(**cambios):
        datos = {**GUIA, **cambios}
        respuesta = cliente.post("/guias", json=datos)
        assert respuesta.status_code == 201, respuesta.json()
        return respuesta.json()["numero"]
    return crear


@pytest.fixture
def avanzar(cliente):
    def mover(numero, hasta):
        for estado, lugar in RUTA:
            r = cliente.post(f"/guias/{numero}/escaneos", json={"nuevo_estado": estado, "ubicacion": lugar})
            assert r.status_code == 200, r.json()
            if estado == hasta:
                return
    return mover
