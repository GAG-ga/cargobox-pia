"""Esquemas Pydantic: forma del JSON de entrada/salida. Swagger se genera a partir de ellos."""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class PersonaIn(BaseModel):
    nombre: str = Field(examples=["Carlos Ruiz"])
    telefono: str = Field(examples=["8112345678"], description="10 dígitos")


class DireccionIn(BaseModel):
    calle: str = Field(examples=["Av. Universidad 100"])
    codigo_postal: str = Field(examples=["66450"], description="5 dígitos")


class PaqueteIn(BaseModel):
    peso_kg: Decimal = Field(examples=[10], description="Máximo 30 kg (RN-01)")
    largo_cm: Decimal = Field(examples=[40], description="Máximo 100 cm por lado (RN-01)")
    ancho_cm: Decimal = Field(examples=[30])
    alto_cm: Decimal = Field(examples=[20])


class RegistrarGuiaIn(BaseModel):
    remitente: PersonaIn
    destinatario: PersonaIn
    origen: DireccionIn
    destino: DireccionIn
    paquete: PaqueteIn
    nivel: Literal["ESTANDAR", "EXPRESS"] = "ESTANDAR"
    valor_declarado: Decimal = Field(examples=[1200])
    sucursal: str = Field(examples=["Sucursal San Nicolás"])


class GuiaOut(BaseModel):
    numero: str
    estado: str
    nivel: str
    tarifa: str
    fecha_estimada: date
    destino: str
    intentos_fallidos: int
    con_garantia: bool
    cargos_adicionales: str
    reembolso: str
    compensacion: str
    mensaje: str = Field(description="Texto entendible para el cliente")


class CorregirDatosIn(BaseModel):
    origen: DireccionIn | None = None
    destino: DireccionIn | None = None


class EscaneoIn(BaseModel):
    nuevo_estado: Literal["CLASIFICADO", "EN_TRANSITO", "CENTRO_DESTINO", "EN_REPARTO"]
    ubicacion: str = Field(examples=["CEDIS Monterrey"])


class IntentoFallidoIn(BaseModel):
    motivo: str = Field(examples=["Destinatario ausente"])
    ubicacion: str = "Domicilio del destinatario"


class EntregaIn(BaseModel):
    firma_digital: str = Field(examples=["firma-ana.png"])
    foto: str = Field(examples=["foto-paquete.jpg"])
    nombre_receptor: str = Field(examples=["Ana López"])
    es_tercero: bool = Field(False, description="True si recibe un vecino o portero (US07)")
    ubicacion: str = "Domicilio del destinatario"


class CambioDireccionIn(BaseModel):
    nueva_direccion: DireccionIn
    identidad_validada: bool = Field(description="Atención al Cliente validó la identidad (RN-14)")


class EstadoPublicoOut(BaseModel):
    numero: str
    estado: str
    fecha_estimada: date
    mensaje: str


class EventoOut(BaseModel):
    estado: str
    ubicacion: str
    fecha_hora: datetime


class HistorialOut(BaseModel):
    numero: str
    estado: str
    fecha_estimada: date
    eventos: list[EventoOut]


class FolioDanoIn(BaseModel):
    numero_guia: str = Field(examples=["CBX-000001"])
    foto: str = Field(examples=["dano.jpg"], description="Evidencia fotográfica obligatoria (RN-17)")


class ResolucionIn(BaseModel):
    resolucion: Literal["REEMBOLSO", "REPOSICION", "ATENDIDA"]


class IncidenciaOut(BaseModel):
    folio: str
    numero_guia: str
    tipo: str
    estado: str
    asignada_a: str
    resolucion: str | None


class MonitoreoOut(BaseModel):
    ejecutado_en: datetime
    alertas_generadas: list[str]
    alertas_escaladas: list[str]
    guias_devueltas: list[str]


class ErrorOut(BaseModel):
    error: str = Field(examples=["CargaEspecialRequerida"])
    mensaje: str = Field(examples=["El paquete excede 30 kg o 100 cm por lado: debe enviarse como "
                                   "carga especial y no puede recibir una guía estándar."])
