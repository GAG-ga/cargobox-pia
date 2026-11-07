"""Caso de uso: ejecutar casos_prueba.csv y transiciones_prueba.csv contra el dominio.

Cada fila sale con `resultado_alumno` y `evidencia` llenos (Secuencia para estudiantes, pasos 4-5).
"""
from collections.abc import Callable

from src.domain.errores import ErrorDominio
from src.domain.estados import EstadoGuia
from src.domain.operacion_servicio import (
    BeneficioReferencia,
    OperacionServicio,
    PuedeProcesarse,
    RemitenteActivo,
)


def _repetir_aprobacion(op: OperacionServicio) -> None:
    op.aprobar()
    op.aprobar()


# accion_sugerida → comando del dominio (interpretación documentada en docs/paquete-docente.md)
ACCIONES: dict[str, Callable[[OperacionServicio], None]] = {
    "aprobar": lambda op: op.aprobar(),
    "cancelar": lambda op: op.cancelar(),
    "completar": lambda op: op.completar(),
    "repetir_aprobacion": _repetir_aprobacion,
    "saltar_estado": lambda op: op.forzar_estado(EstadoGuia.EN_TRANSITO),
}


def evaluar_caso(fila: dict[str, str], operaciones: dict[str, OperacionServicio]) -> dict[str, str]:
    op = operaciones[fila["operacion_id"]]
    if fila["tipo_prueba"] == "validar_operacion":
        cumple = PuedeProcesarse().es_satisfecha_por(op)
        evidencia = (f"activo={int(RemitenteActivo().es_satisfecha_por(op))}; "
                     f"lineas={len(op.lineas)}; autorizado={int(op.autorizada)}")
    elif fila["tipo_prueba"] == "evaluar_beneficio":
        cumple = BeneficioReferencia().es_satisfecha_por(op)
        evidencia = (f"preferente={int(op.remitente.preferente)}; total={op.total.monto}; "
                     f"promocion={int(op.promocion_activa)}")
    else:
        raise ValueError(f"tipo_prueba desconocido: {fila['tipo_prueba']}")
    return {**fila, "resultado_alumno": "CUMPLE" if cumple else "NO_CUMPLE", "evidencia": evidencia}


def ejecutar_transicion(fila: dict[str, str], operaciones: dict[str, OperacionServicio]) -> dict[str, str]:
    op = operaciones[fila["operacion_id"]]
    if op.estado.value != fila["estado_inicial"]:
        raise ValueError(f"{op.operacion_id} no está en {fila['estado_inicial']}")
    excepcion = "—"
    try:
        ACCIONES[fila["accion_sugerida"]](op)
    except ErrorDominio as error:
        excepcion = type(error).__name__ + (f" ({error.detalle})" if error.detalle else "")
    eventos = ", ".join(f"{type(e).__name__}({getattr(e, 'estado', '')})".replace("()", "")
                        for e in op.eventos) or "—"
    resultado = "OK" if excepcion == "—" else "RECHAZADA"
    return {**fila, "resultado_alumno": resultado, "estado_final": op.estado.value,
            "eventos": eventos, "excepcion": excepcion}


def ejecutar_paquete(casos: list[dict[str, str]], transiciones: list[dict[str, str]],
                     cargar: Callable[[], dict[str, OperacionServicio]]):
    """Los casos de reglas no cambian estado; cada transición se ejecuta sobre datos recién cargados."""
    operaciones = cargar()
    resultados_casos = [evaluar_caso(f, operaciones) for f in casos]
    resultados_trans = [ejecutar_transicion(f, cargar()) for f in transiciones]
    return resultados_casos, resultados_trans
