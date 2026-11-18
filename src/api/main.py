"""Punto de entrada: crea la aplicación FastAPI. Swagger UI queda en /docs y el panel en /panel."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.dependencias import Contenedor
from src.api.errores import registrar_manejadores
from src.api.rutas import consultas, guias, incidencias
from src.infrastructure.config import Configuracion

# Carpeta del dashboard en HTML (frontend/index.html), en la raíz del proyecto.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

DESCRIPCION = """
API de **CargoBox — Plataforma de Envíos Nacionales** (Caso 14, PIA Componentes de Lógica de Negocios).

Implementa las 15 historias de usuario del BRD con DDD, Specification y State Machine.
Cada endpoint indica su historia (US) en el título. Los errores de negocio responden con
`{"error": "...", "mensaje": "..."}` en lenguaje entendible para el cliente.

El panel de operaciones (dashboard en HTML) está en [`/panel`](/panel).
"""


def crear_app(config: Configuracion | None = None) -> FastAPI:
    app = FastAPI(title="CargoBox API", version="1.0.0", description=DESCRIPCION)
    app.state.contenedor = Contenedor(config or Configuracion.desde_entorno())
    # CORS: permite abrir frontend/index.html directamente desde el navegador (file://)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    registrar_manejadores(app)
    app.include_router(guias.router)
    app.include_router(consultas.router)
    app.include_router(incidencias.router)
    app.mount("/panel", StaticFiles(directory=FRONTEND_DIR, html=True), name="panel")

    @app.get("/", include_in_schema=False)
    def inicio():
        return RedirectResponse("/docs")

    @app.get("/salud", tags=["Sistema"], summary="Verificar que la API está activa")
    def salud():
        return {"estado": "ok", "entorno": app.state.contenedor.config.app_env}

    return app


app = crear_app()
