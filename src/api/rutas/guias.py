"""Endpoints de guías: comandos que cambian el estado (US01–US07, US10, US11, US15)."""
from fastapi import APIRouter, Depends, status

from src.api.dependencias import (
    servicio_entregas,
    servicio_envios,
    servicio_incidencias,
    servicio_rastreo,
)
from src.api.esquemas import (
    CambioDireccionIn,
    CorregirDatosIn,
    EntregaIn,
    ErrorOut,
    EscaneoIn,
    GuiaOut,
    IntentoFallidoIn,
    RegistrarGuiaIn,
)
from src.application.comandos import (
    CambiarDireccionCommand,
    CapturarEvidenciaCommand,
    RegistrarEscaneoCommand,
    RegistrarGuiaCommand,
)

router = APIRouter(prefix="/guias", tags=["Guías"])

ERRORES = {404: {"model": ErrorOut, "description": "La guía no existe"},
           409: {"model": ErrorOut, "description": "Una regla del negocio no lo permite"},
           422: {"model": ErrorOut, "description": "Datos inválidos o incompletos"}}


# ============================================================================================
# EJEMPLO COMPLETO — US01 Registro de envío y generación de guía (RN-01, RN-02, RN-03, RN-20)
#
# Todo endpoint sigue los mismos 4 pasos:
#   1. Declarar la ruta, el método HTTP y el esquema de respuesta (Swagger los muestra).
#   2. Recibir el servicio de aplicación con Depends(...) — inyección de dependencias.
#   3. Convertir el JSON (esquema Pydantic) en un Command y llamar UN método del servicio.
#   4. Devolver el DTO. Los errores de negocio NO se atrapan aquí: los traduce api/errores.py
#      a un JSON con "error" y "mensaje" para el cliente.
# ============================================================================================
@router.post("", status_code=status.HTTP_201_CREATED, response_model=GuiaOut, responses=ERRORES,
             summary="US01 · Registrar un envío y generar su guía")
def registrar_guia(datos: RegistrarGuiaIn, servicio=Depends(servicio_envios)):  # paso 1 y 2
    comando = RegistrarGuiaCommand(                                               # paso 3
        remitente_nombre=datos.remitente.nombre, remitente_telefono=datos.remitente.telefono,
        destinatario_nombre=datos.destinatario.nombre,
        destinatario_telefono=datos.destinatario.telefono,
        origen_calle=datos.origen.calle, origen_cp=datos.origen.codigo_postal,
        destino_calle=datos.destino.calle, destino_cp=datos.destino.codigo_postal,
        peso_kg=datos.paquete.peso_kg, largo_cm=datos.paquete.largo_cm,
        ancho_cm=datos.paquete.ancho_cm, alto_cm=datos.paquete.alto_cm,
        nivel=datos.nivel, valor_declarado=datos.valor_declarado, sucursal=datos.sucursal)
    return servicio.registrar_guia(comando)                                       # paso 4


@router.post("/{numero}/cancelacion", response_model=GuiaOut, responses=ERRORES,
             summary="US02 · Cancelar una guía antes de clasificarla")
def cancelar(numero: str, servicio=Depends(servicio_envios)):
    return servicio.cancelar(numero)


@router.patch("/{numero}/datos", response_model=GuiaOut, responses=ERRORES,
              summary="US03 · Corregir origen o destino antes de clasificar")
def corregir_datos(numero: str, datos: CorregirDatosIn, servicio=Depends(servicio_envios)):
    origen = (datos.origen.calle, datos.origen.codigo_postal) if datos.origen else None
    destino = (datos.destino.calle, datos.destino.codigo_postal) if datos.destino else None
    return servicio.corregir_datos(numero, origen=origen, destino=destino)


@router.post("/{numero}/escaneos", response_model=GuiaOut, responses=ERRORES,
             summary="US04 · Registrar escaneo en centro de distribución")
def registrar_escaneo(numero: str, datos: EscaneoIn, servicio=Depends(servicio_rastreo)):
    return servicio.registrar_escaneo(RegistrarEscaneoCommand(numero, datos.nuevo_estado,
                                                              datos.ubicacion))


@router.post("/{numero}/intentos-fallidos", response_model=GuiaOut, responses=ERRORES,
             summary="US05 · Registrar intento de entrega fallido")
def registrar_intento_fallido(numero: str, datos: IntentoFallidoIn,
                              servicio=Depends(servicio_entregas)):
    return servicio.registrar_intento_fallido(numero, datos.motivo, datos.ubicacion)


@router.post("/{numero}/entrega", response_model=GuiaOut, responses=ERRORES,
             summary="US06 / US07 / US10 · Entregar con firma y foto (también a tercero o en centro)")
def capturar_evidencia(numero: str, datos: EntregaIn, servicio=Depends(servicio_entregas)):
    return servicio.capturar_evidencia_entrega(CapturarEvidenciaCommand(
        numero, datos.firma_digital, datos.foto, datos.nombre_receptor, datos.es_tercero,
        datos.ubicacion))


@router.post("/{numero}/reagendamiento", response_model=GuiaOut, responses=ERRORES,
             summary="US10 · Reagendar la visita durante el resguardo")
def reagendar(numero: str, servicio=Depends(servicio_entregas)):
    return servicio.reagendar(numero)


@router.patch("/{numero}/direccion", response_model=GuiaOut, responses=ERRORES,
              summary="US11 · Cambiar dirección en tránsito (+$80, sin garantía)")
def cambiar_direccion(numero: str, datos: CambioDireccionIn, servicio=Depends(servicio_envios)):
    return servicio.cambiar_direccion(CambiarDireccionCommand(
        numero, datos.nueva_direccion.calle, datos.nueva_direccion.codigo_postal,
        datos.identidad_validada))


@router.post("/{numero}/perdida", response_model=GuiaOut, responses=ERRORES,
             summary="US15 · Declarar pérdida y calcular compensación")
def declarar_perdida(numero: str, servicio=Depends(servicio_incidencias)):
    return servicio.declarar_perdida(numero)
