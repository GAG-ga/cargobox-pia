"""Dobles de prueba: implementaciones en memoria de los puertos (Liskov: mismos contratos)."""
from datetime import UTC, datetime, timedelta

from src.application.puertos import UnitOfWork
from src.domain.incidencia import EstadoIncidencia, Incidencia
from src.domain.value_objects import NumeroGuia


class GuiaRepositoryEnMemoria:
    def __init__(self):
        self.datos, self._seq = {}, 0

    def siguiente_numero(self):
        self._seq += 1
        return NumeroGuia.desde_secuencia(self._seq)

    def por_numero(self, numero):
        return self.datos.get(numero)

    def guardar(self, guia):
        self.datos[guia.numero.valor] = guia

    def en_estados(self, estados):
        return [g for g in self.datos.values() if g.estado in estados]


class IncidenciaRepositoryEnMemoria:
    def __init__(self):
        self.datos, self._seq = {}, 0

    def siguiente_folio(self):
        self._seq += 1
        return Incidencia.folio_desde_secuencia(self._seq)

    def por_folio(self, folio):
        return self.datos.get(folio)

    def guardar(self, inc):
        self.datos[inc.folio] = inc

    def pendientes(self):
        return [i for i in self.datos.values() if i.estado != EstadoIncidencia.RESUELTA]

    def abiertas(self, tipo=None):
        return [i for i in self.datos.values() if i.estado == EstadoIncidencia.ABIERTA
                and (tipo is None or i.tipo == tipo)]


class UnitOfWorkEnMemoria(UnitOfWork):
    def __init__(self):
        self.guias = GuiaRepositoryEnMemoria()
        self.incidencias = IncidenciaRepositoryEnMemoria()
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class RelojFijo:
    def __init__(self, inicio=datetime(2026, 11, 2, 9, 0, tzinfo=UTC)):  # lunes
        self.actual = inicio

    def ahora(self):
        return self.actual

    def avanzar(self, **kwargs):
        self.actual += timedelta(**kwargs)

    def fijar(self, momento):
        self.actual = momento


class PublicadorEnMemoria:
    def __init__(self):
        self.eventos = []

    def publicar(self, eventos):
        self.eventos.extend(eventos)

    def tipos(self):
        return [type(e).__name__ for e in self.eventos]


class LectorHistorialEnMemoria:
    """HistorialRastreoReader sobre el repositorio en memoria (lado de lectura)."""

    def __init__(self, repo: GuiaRepositoryEnMemoria):
        self.repo = repo

    def estado_publico(self, numero):
        g = self.repo.por_numero(numero)
        if g is None:
            return None
        return {"numero": numero, "estado": g.estado.value, "fecha_estimada": g.fecha_estimada}

    def historial(self, numero):
        g = self.repo.por_numero(numero)
        if g is None:
            return None
        return {"numero": numero, "estado": g.estado.value, "fecha_estimada": g.fecha_estimada,
                "telefono_remitente": g.remitente.telefono,
                "eventos": [{"estado": e.estado.value, "ubicacion": e.ubicacion,
                             "fecha_hora": e.fecha_hora} for e in g.eventos]}
