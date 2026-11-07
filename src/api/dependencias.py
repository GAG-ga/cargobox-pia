"""Ensamblado (inyección de dependencias): aquí se conectan los puertos con sus adaptadores."""
from datetime import datetime

from fastapi import Request

from src.application.puertos import RelojSistema
from src.application.servicios import (
    ConsultaRastreoQueryService,
    EntregaApplicationService,
    EnvioApplicationService,
    IncidenciaApplicationService,
    RastreoApplicationService,
)
from src.infrastructure.almacen_evidencias import AlmacenEvidenciasDisco
from src.infrastructure.config import Configuracion
from src.infrastructure.db import crear_engine, crear_fabrica_sesiones
from src.infrastructure.lector_historial_sql import SqlHistorialRastreoReader
from src.infrastructure.publicador import publicador_con_notificaciones
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


class RelojFijo:
    """Para la demo: ejecutar el monitoreo con una fecha simulada (ADR-011)."""

    def __init__(self, momento: datetime):
        self.momento = momento

    def ahora(self) -> datetime:
        return self.momento


class Contenedor:
    def __init__(self, config: Configuracion):
        self.config = config
        self.engine = crear_engine(config.database_url)
        self.sesiones = crear_fabrica_sesiones(self.engine)
        self.publicador, self.notificaciones = publicador_con_notificaciones()
        self.reloj = RelojSistema()
        self.almacen = AlmacenEvidenciasDisco(config.evidencias_dir)

    def _args(self, reloj=None):
        return SqlAlchemyUnitOfWork(self.sesiones), self.publicador, reloj or self.reloj

    def envios(self):
        return EnvioApplicationService(*self._args())

    def rastreo(self):
        return RastreoApplicationService(*self._args())

    def entregas(self):
        return EntregaApplicationService(*self._args(), self.almacen)

    def incidencias(self, ahora: datetime | None = None):
        return IncidenciaApplicationService(*self._args(RelojFijo(ahora) if ahora else None))

    def consultas(self):
        return ConsultaRastreoQueryService(SqlHistorialRastreoReader(self.sesiones))


def contenedor(request: Request) -> Contenedor:
    return request.app.state.contenedor


def servicio_envios(request: Request) -> EnvioApplicationService:
    return contenedor(request).envios()


def servicio_rastreo(request: Request) -> RastreoApplicationService:
    return contenedor(request).rastreo()


def servicio_entregas(request: Request) -> EntregaApplicationService:
    return contenedor(request).entregas()


def servicio_incidencias(request: Request) -> IncidenciaApplicationService:
    return contenedor(request).incidencias()


def servicio_consultas(request: Request) -> ConsultaRastreoQueryService:
    return contenedor(request).consultas()
