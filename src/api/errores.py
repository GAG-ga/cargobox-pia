"""Traduce errores de dominio a respuestas HTTP con un mensaje que el cliente entiende."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.application.errores import AccesoDenegado, GuiaNoEncontrada, IncidenciaNoEncontrada
from src.domain.errores import (
    CargaEspecialRequerida,
    DatoInvalido,
    ErrorDominio,
    EvidenciaIncompleta,
    IdentidadNoValidada,
)

CODIGOS = [
    ((GuiaNoEncontrada, IncidenciaNoEncontrada), 404),
    ((AccesoDenegado,), 403),
    ((DatoInvalido, CargaEspecialRequerida, EvidenciaIncompleta, IdentidadNoValidada), 422),
]


def codigo_http(error: ErrorDominio) -> int:
    for tipos, codigo in CODIGOS:
        if isinstance(error, tipos):
            return codigo
    return 409  # la petición es válida pero una regla del negocio no lo permite


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorDominio)
    async def error_de_negocio(_: Request, exc: ErrorDominio):
        mensaje = exc.mensaje
        if isinstance(exc, DatoInvalido) and exc.detalle:
            mensaje = exc.detalle
        return JSONResponse(status_code=codigo_http(exc),
                            content={"error": type(exc).__name__, "mensaje": mensaje})

    @app.exception_handler(RequestValidationError)
    async def error_de_formato(_: Request, exc: RequestValidationError):
        campos = [".".join(str(p) for p in e["loc"][1:]) for e in exc.errors()]
        return JSONResponse(status_code=422, content={
            "error": "DatosIncompletos",
            "mensaje": f"Revisa los datos enviados. Campos con problema: {', '.join(campos)}."})
