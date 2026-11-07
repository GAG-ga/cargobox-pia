"""Paquete de datos del docente: Specifications, máquina de estados y ejecución de los CSV."""
from decimal import Decimal
from pathlib import Path

import pytest

from src.application.validacion_paquete import ejecutar_paquete, ejecutar_transicion, evaluar_caso
from src.domain.errores import DatoInvalido, OperacionNoProcesable, TransicionEstadoInvalida
from src.domain.estados import EstadoGuia as E
from src.domain.eventos import EntregaCompletada, EstadoCambiado
from src.domain.operacion_servicio import (
    BeneficioReferencia,
    LineaOperacion,
    OperacionServicio,
    PuedeProcesarse,
    Remitente,
    ServicioCatalogo,
    ServiciosConCapacidad,
)
from src.domain.value_objects import Dinero
from src.infrastructure.datos_csv import cargar_operaciones, escribir_csv, leer_csv

DATOS = Path(__file__).resolve().parents[2] / "datos"


def servicio(precio="500", capacidad=10, habilitado=True, rid="P1"):
    return ServicioCatalogo(rid, "Paquete", Dinero(Decimal(precio)), capacidad, habilitado)


def operacion(activo=True, preferente=True, lineas=None, promo=False, autorizada=True):
    if lineas is None:
        lineas = [LineaOperacion(servicio("500"), 3)]
    return OperacionServicio("OP-1", Remitente("C1", activo, preferente), lineas, promo, autorizada)


# --- Total con Decimal ------------------------------------------------------------------
def test_total_suma_precio_por_cantidad_con_decimal():
    op = operacion(lineas=[LineaOperacion(servicio("543.10"), 3), LineaOperacion(servicio("0.05"), 1)])
    assert op.total == Dinero(Decimal("1629.35"))


def test_cantidad_debe_ser_positiva():
    with pytest.raises(DatoInvalido):
        LineaOperacion(servicio(), 0)


# --- Specifications ---------------------------------------------------------------------
@pytest.mark.parametrize("cambios, esperado", [
    ({}, True),
    ({"activo": False}, False),
    ({"lineas": []}, False),
    ({"autorizada": False}, False),
])
def test_puede_procesarse_and(cambios, esperado):
    assert PuedeProcesarse().es_satisfecha_por(operacion(**cambios)) is esperado


@pytest.mark.parametrize("cambios, esperado", [
    ({}, True),                                                     # 3 × 500 = 1500 (límite)
    ({"preferente": False}, False),
    ({"promo": True}, False),                                       # NOT promoción
    ({"lineas": [LineaOperacion(servicio("499.99"), 3)]}, False),  # 1499.97 < 1500
])
def test_beneficio_referencia_and_not(cambios, esperado):
    assert BeneficioReferencia().es_satisfecha_por(operacion(**cambios)) is esperado


def test_combinacion_or_de_specifications():
    cualquiera = BeneficioReferencia() | PuedeProcesarse()
    assert cualquiera.es_satisfecha_por(operacion(preferente=False))
    assert not cualquiera.es_satisfecha_por(operacion(preferente=False, autorizada=False))


@pytest.mark.parametrize("serv, cantidad, esperado", [
    (servicio(capacidad=5), 5, True),
    (servicio(capacidad=5), 6, False),
    (servicio(habilitado=False), 1, False),
])
def test_servicios_con_capacidad(serv, cantidad, esperado):
    op = operacion(lineas=[LineaOperacion(serv, cantidad)])
    assert ServiciosConCapacidad().es_satisfecha_por(op) is esperado


# --- Máquina de estados y eventos --------------------------------------------------------
def test_aprobar_pasa_a_clasificado_y_publica_evento():
    op = operacion()
    op.aprobar()
    assert op.estado == E.CLASIFICADO
    assert op.eventos[-1] == EstadoCambiado("OP-1", op.eventos[-1].ocurrido_en, "CLASIFICADO")


def test_completar_recorre_todos_los_estados():
    op = operacion()
    op.completar()
    assert op.estado == E.ENTREGADO
    assert [e.estado for e in op.eventos if isinstance(e, EstadoCambiado)] == [
        "CLASIFICADO", "EN_TRANSITO", "CENTRO_DESTINO", "EN_REPARTO", "ENTREGADO"]
    assert isinstance(op.eventos[-1], EntregaCompletada)


def test_aprobar_sin_precondiciones_lanza_error_con_motivos():
    op = operacion(activo=False, lineas=[LineaOperacion(servicio(habilitado=False), 1)], autorizada=False)
    with pytest.raises(OperacionNoProcesable) as error:
        op.aprobar()
    assert error.value.detalle == ("remitente inactivo; sin autorización; "
                                   "servicio deshabilitado o sin capacidad")
    assert op.estado == E.RECIBIDO and op.eventos == []
    assert operacion(lineas=[]).motivos_rechazo() == ["sin servicios"]


def test_saltar_estado_y_repetir_aprobacion_son_invalidos():
    op = operacion()
    with pytest.raises(TransicionEstadoInvalida):
        op.forzar_estado(E.EN_TRANSITO)
    op.aprobar()
    with pytest.raises(TransicionEstadoInvalida):
        op.aprobar()


def test_cancelar_solo_desde_recibido():
    op = operacion()
    op.cancelar()
    assert op.estado == E.CANCELADO
    with pytest.raises(TransicionEstadoInvalida):
        op.cancelar()


# --- Lector CSV (claves foráneas) ---------------------------------------------------------
def test_carga_las_60_operaciones_del_paquete():
    ops = cargar_operaciones(DATOS)
    assert len(ops) == 60
    assert sum(len(o.lineas) for o in ops.values()) == 117
    assert all(o.estado == E.RECIBIDO for o in ops.values())
    # CAR-O001: P009 (1,111) × 3 + P014 (1,466) × 4
    assert ops["CAR-O001"].total == Dinero(Decimal("9197.00"))


def _copiar_datos(destino: Path, **reemplazos):
    for archivo in DATOS.glob("*.csv"):
        filas = leer_csv(archivo)
        if archivo.name in reemplazos:
            filas = reemplazos[archivo.name](filas)
        escribir_csv(destino / archivo.name, filas)


def test_detecta_recurso_inexistente(tmp_path):
    extra = {"operacion_id": "CAR-O001", "recurso_id": "X", "cantidad": "1"}
    _copiar_datos(tmp_path, **{"detalle_operaciones.csv": lambda f: f + [extra]})
    with pytest.raises(DatoInvalido, match="Recurso inexistente"):
        cargar_operaciones(tmp_path)


def test_detecta_actor_inexistente(tmp_path):
    def cambiar(filas):
        filas[0]["actor_id"] = "NO-EXISTE"
        return filas
    _copiar_datos(tmp_path, **{"operaciones.csv": cambiar})
    with pytest.raises(DatoInvalido, match="Actor inexistente"):
        cargar_operaciones(tmp_path)


def test_detecta_detalle_de_operacion_inexistente(tmp_path):
    extra = {"operacion_id": "OP-X", "recurso_id": "CAR-P001", "cantidad": "1"}
    _copiar_datos(tmp_path, **{"detalle_operaciones.csv": lambda f: f + [extra]})
    with pytest.raises(DatoInvalido, match="operaciones inexistentes"):
        cargar_operaciones(tmp_path)


# --- Ejecución de casos_prueba.csv y transiciones_prueba.csv ------------------------------
@pytest.fixture(scope="module")
def resultados():
    return ejecutar_paquete(leer_csv(DATOS / "casos_prueba.csv"),
                            leer_csv(DATOS / "transiciones_prueba.csv"),
                            lambda: cargar_operaciones(DATOS))


def test_se_ejecutan_los_120_casos_y_20_transiciones(resultados):
    casos, trans = resultados
    assert len(casos) == 120 and len(trans) == 20
    assert all(c["resultado_alumno"] in {"CUMPLE", "NO_CUMPLE"} for c in casos)
    assert all(t["resultado_alumno"] in {"OK", "RECHAZADA"} for t in trans)


def test_resultados_conocidos_de_casos(resultados):
    casos = {c["caso_id"]: c for c in resultados[0]}
    assert casos["CAR-T001"]["resultado_alumno"] == "CUMPLE"
    assert casos["CAR-T013"]["resultado_alumno"] == "NO_CUMPLE"     # operación sin líneas
    assert casos["CAR-T013"]["evidencia"] == "activo=1; lineas=0; autorizado=1"
    assert casos["CAR-B001"]["resultado_alumno"] == "NO_CUMPLE"     # remitente no preferente


def test_resultados_conocidos_de_transiciones(resultados):
    trans = {t["caso_id"]: t for t in resultados[1]}
    assert (trans["CAR-S001"]["estado_final"], trans["CAR-S001"]["excepcion"]) == ("ENTREGADO", "—")
    assert trans["CAR-S002"]["estado_final"] == "CANCELADO"
    assert trans["CAR-S003"]["estado_final"] == "CLASIFICADO"
    assert trans["CAR-S003"]["excepcion"].startswith("TransicionEstadoInvalida")
    assert trans["CAR-S004"]["estado_final"] == "RECIBIDO"
    assert trans["CAR-S005"]["excepcion"] == ("OperacionNoProcesable "
                                              "(servicio deshabilitado o sin capacidad)")


def test_tipo_de_prueba_desconocido():
    with pytest.raises(ValueError):
        evaluar_caso({"operacion_id": "OP-1", "tipo_prueba": "otro"}, {"OP-1": operacion()})


def test_transicion_con_estado_inicial_distinto():
    op = operacion()
    op.aprobar()
    with pytest.raises(ValueError):
        ejecutar_transicion({"operacion_id": "OP-1", "estado_inicial": "RECIBIDO",
                             "accion_sugerida": "aprobar"}, {"OP-1": op})
