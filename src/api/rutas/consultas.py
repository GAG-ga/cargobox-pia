"""Rastreo público: lado de lectura (CQRS) para destinatario y remitente (US08, US09)."""
from fastapi import APIRouter, Depends, Query

from src.api.dependencias import servicio_consultas
from src.api.esquemas import ErrorOut, EstadoPublicoOut, HistorialOut

router = APIRouter(prefix="/rastreo", tags=["Rastreo público"])


@router.get("/{numero}", response_model=EstadoPublicoOut, responses={404: {"model": ErrorOut}},
            summary="US08 · Estado actual y fecha estimada para el destinatario")
def estado_publico(numero: str, servicio=Depends(servicio_consultas)):
    return servicio.estado_publico(numero)


@router.get("/{numero}/historial", response_model=HistorialOut,
            responses={403: {"model": ErrorOut}, 404: {"model": ErrorOut}},
            summary="US09 · Historial completo para el remitente")
def historial(numero: str, telefono: str = Query(description="Teléfono del remitente (RN-08)"),
              servicio=Depends(servicio_consultas)):
    return servicio.historial(numero, telefono)
