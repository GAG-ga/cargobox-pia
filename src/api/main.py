"""Punto de entrada: crea la aplicación FastAPI. Swagger UI queda en /docs."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api.dependencias import Contenedor
from src.api.errores import registrar_manejadores
from src.api.rutas import consultas, guias, incidencias
from src.infrastructure.config import Configuracion

DESCRIPCION = """
API de **CargoBox — Plataforma de Envíos Nacionales** (Caso 14, PIA Componentes de Lógica de Negocios).

Implementa las 15 historias de usuario del BRD con DDD, Specification y State Machine.
Cada endpoint indica su historia (US) en el título. Los errores de negocio responden con
`{"error": "...", "mensaje": "..."}` en lenguaje entendible para el cliente.
"""


def crear_app(config: Configuracion | None = None) -> FastAPI:
    app = FastAPI(title="CargoBox API", version="1.0.0", description=DESCRIPCION)
    app.state.contenedor = Contenedor(config or Configuracion.desde_entorno())
    registrar_manejadores(app)
    app.include_router(guias.router)
    app.include_router(consultas.router)
    app.include_router(incidencias.router)

    @app.get("/", include_in_schema=False)
    def inicio():
        return RedirectResponse("/docs")

    @app.get("/salud", tags=["Sistema"], summary="Verificar que la API está activa")
    def salud():
        return {"estado": "ok", "entorno": app.state.contenedor.config.app_env}

    return app


app = crear_app()
