"""Integración con base de datos: el agregado se guarda y se reconstruye igual (round-trip)."""
from datetime import UTC, datetime
from decimal import Decimal

from src.domain.estados import EstadoGuia
from src.domain.guia import Guia
from src.domain.incidencia import Incidencia, Resolucion
from src.domain.value_objects import (
    Dimensiones,
    Dinero,
    Direccion,
    EvidenciaEntrega,
    NivelServicio,
    Paquete,
    Persona,
    Peso,
)
from src.infrastructure.almacen_evidencias import AlmacenEvidenciasDisco
from src.infrastructure.config import Configuracion
from src.infrastructure.db import crear_engine, crear_fabrica_sesiones
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from tests.api.conftest import base_limpia, url_de_pruebas

AHORA = datetime(2026, 11, 2, 9, tzinfo=UTC)


def uow_nuevo():
    url = base_limpia(url_de_pruebas())
    return SqlAlchemyUnitOfWork(crear_fabrica_sesiones(crear_engine(url)))


def guia(numero):
    return Guia.generar(numero, Persona("Carlos", "8112345678"), Persona("Ana", "8187654321"),
                        Direccion("Av. 1", "66450"), Direccion("Roble 10", "66220"),
                        Paquete(Peso(10), Dimensiones(40, 30, 20)), NivelServicio.ESTANDAR,
                        Dinero(Decimal("1200")), Dinero(Decimal("249")), "Sucursal Centro", AHORA)


def test_guia_se_guarda_y_reconstruye_con_historial():
    uow = uow_nuevo()
    with uow:
        g = guia(uow.guias.siguiente_numero())
        for estado in (EstadoGuia.CLASIFICADO, EstadoGuia.EN_TRANSITO, EstadoGuia.CENTRO_DESTINO,
                       EstadoGuia.EN_REPARTO):
            g.registrar_escaneo(estado, "CEDIS", AHORA)
        g.registrar_intento_fallido("ausente", "Domicilio", AHORA)
        g.registrar_entrega(EvidenciaEntrega("f.png", "f.jpg", "Ana", True), "Domicilio", AHORA)
        uow.guias.guardar(g)
        uow.commit()
    with uow:
        leida = uow.guias.por_numero("CBX-000001")
        assert leida.estado == EstadoGuia.ENTREGADO
        assert len(leida.eventos) == 6 and len(leida.intentos) == 2
        assert leida.evidencia.es_tercero is True
        assert leida.creada_en.tzinfo is not None
        assert uow.guias.en_estados({EstadoGuia.ENTREGADO})[0].numero == g.numero


def test_rollback_no_guarda_nada():
    uow = uow_nuevo()
    with uow:
        uow.guias.guardar(guia(uow.guias.siguiente_numero()))
        uow.rollback()
    with uow:
        assert uow.guias.por_numero("CBX-000001") is None


def test_incidencias_se_guardan_y_filtran():
    uow = uow_nuevo()
    with uow:
        uow.guias.guardar(guia(uow.guias.siguiente_numero()))
        alerta = Incidencia.abrir_alerta_retraso(uow.incidencias.siguiente_folio(), "CBX-000001", AHORA)
        dano = Incidencia.abrir_folio_dano(uow.incidencias.siguiente_folio(), "CBX-000001", "d.jpg",
                                           "Sucursal Centro", AHORA)
        dano.resolver(Resolucion.REEMBOLSO)
        uow.incidencias.guardar(alerta)
        uow.incidencias.guardar(dano)
        uow.commit()
    with uow:
        assert [i.folio for i in uow.incidencias.abiertas()] == ["INC-000001"]
        assert uow.incidencias.por_folio("INC-000002").resolucion == Resolucion.REEMBOLSO
        assert uow.incidencias.por_folio("INC-999999") is None


def test_configuracion_desde_entorno(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@h:5432/db")
    assert Configuracion.desde_entorno().database_url.startswith("postgresql+psycopg://")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/db")
    assert Configuracion.desde_entorno().database_url.startswith("postgresql+psycopg://")
    monkeypatch.delenv("DATABASE_URL")
    assert Configuracion.desde_entorno().database_url.startswith("sqlite")


def test_almacen_evidencias_en_disco(tmp_path):
    ruta = AlmacenEvidenciasDisco(str(tmp_path)).guardar("CBX-000001", "firma", "foto")
    assert (tmp_path / "CBX-000001" / "foto.txt").read_text(encoding="utf-8") == "foto"
    assert ruta.endswith("CBX-000001")
