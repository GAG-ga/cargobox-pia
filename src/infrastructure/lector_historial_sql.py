"""Lado de lectura (CQRS, ADR-003): consulta directa, sin reconstruir el agregado."""
from sqlalchemy import select

from src.infrastructure.db import como_utc
from src.infrastructure.modelos import EventoRastreoModel, GuiaModel


class SqlHistorialRastreoReader:
    def __init__(self, fabrica_sesiones):
        self.fabrica_sesiones = fabrica_sesiones

    def estado_publico(self, numero: str) -> dict | None:
        with self.fabrica_sesiones() as s:
            fila = s.execute(select(GuiaModel.numero, GuiaModel.estado, GuiaModel.fecha_estimada)
                             .where(GuiaModel.numero == numero)).first()
            if fila is None:
                return None
            return {"numero": fila.numero, "estado": fila.estado, "fecha_estimada": fila.fecha_estimada}

    def historial(self, numero: str) -> dict | None:
        with self.fabrica_sesiones() as s:
            g = s.execute(select(GuiaModel.numero, GuiaModel.estado, GuiaModel.fecha_estimada,
                                 GuiaModel.remitente_telefono).where(GuiaModel.numero == numero)).first()
            if g is None:
                return None
            eventos = s.execute(select(EventoRastreoModel).where(
                EventoRastreoModel.numero_guia == numero).order_by(EventoRastreoModel.orden)).scalars()
            return {"numero": g.numero, "estado": g.estado, "fecha_estimada": g.fecha_estimada,
                    "telefono_remitente": g.remitente_telefono,
                    "eventos": [{"estado": e.estado, "ubicacion": e.ubicacion,
                                 "fecha_hora": como_utc(e.fecha_hora)} for e in eventos]}
