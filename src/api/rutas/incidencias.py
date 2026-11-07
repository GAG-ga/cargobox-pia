"""Incidencias y monitoreo de reglas de tiempo (US10, US12–US14, ADR-011)."""
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, Request, status

from src.api.dependencias import contenedor, servicio_incidencias
from src.api.esquemas import ErrorOut, FolioDanoIn, IncidenciaOut, MonitoreoOut, ResolucionIn

router = APIRouter(tags=["Incidencias y monitoreo"])
ERRORES = {404: {"model": ErrorOut}, 409: {"model": ErrorOut}, 422: {"model": ErrorOut}}


@router.get("/incidencias", response_model=list[IncidenciaOut],
            summary="US12 · US13 · Ver alertas e incidencias pendientes (abiertas y escaladas)")
def listar_pendientes(servicio=Depends(servicio_incidencias)):
    return servicio.listar_pendientes()


@router.post("/incidencias/danos", status_code=status.HTTP_201_CREATED, response_model=IncidenciaOut,
             responses=ERRORES, summary="US14 · Abrir folio por paquete dañado")
def abrir_folio_dano(datos: FolioDanoIn, servicio=Depends(servicio_incidencias)):
    return servicio.abrir_folio_dano(datos.numero_guia, datos.foto)


@router.post("/incidencias/{folio}/resolucion", response_model=IncidenciaOut, responses=ERRORES,
             summary="US14 · Resolver incidencia (reembolso / reposición / atendida)")
def resolver(folio: str, datos: ResolucionIn, servicio=Depends(servicio_incidencias)):
    return servicio.resolver(folio, datos.resolucion)


@router.post("/monitoreo/ejecutar", response_model=MonitoreoOut,
             summary="US10 · US12 · US13 · Ejecutar reglas de tiempo (alertas, escalamiento, resguardos)")
def ejecutar_monitoreo(request: Request, ahora: datetime | None = Query(
        None, description="Fecha simulada para la demo (ISO 8601). Vacío = hora actual.")):
    momento = (ahora.replace(tzinfo=ahora.tzinfo or UTC)) if ahora else datetime.now(UTC)
    resumen = contenedor(request).incidencias(momento).ejecutar_monitoreo()
    return MonitoreoOut(ejecutado_en=momento, alertas_generadas=resumen.alertas_generadas,
                        alertas_escaladas=resumen.alertas_escaladas,
                        guias_devueltas=resumen.guias_devueltas)
