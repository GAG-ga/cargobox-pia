"""Commands: datos simples que llegan a los casos de uso que cambian estado."""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RegistrarGuiaCommand:  # US01
    remitente_nombre: str
    remitente_telefono: str
    destinatario_nombre: str
    destinatario_telefono: str
    origen_calle: str
    origen_cp: str
    destino_calle: str
    destino_cp: str
    peso_kg: Decimal
    largo_cm: Decimal
    ancho_cm: Decimal
    alto_cm: Decimal
    nivel: str
    valor_declarado: Decimal
    sucursal: str


@dataclass(frozen=True)
class RegistrarEscaneoCommand:  # US04
    numero_guia: str
    nuevo_estado: str
    ubicacion: str


@dataclass(frozen=True)
class CapturarEvidenciaCommand:  # US06, US07, US10
    numero_guia: str
    firma_digital: str
    foto: str
    nombre_receptor: str
    es_tercero: bool = False
    ubicacion: str = "Domicilio del destinatario"


@dataclass(frozen=True)
class CambiarDireccionCommand:  # US11
    numero_guia: str
    calle: str
    codigo_postal: str
    identidad_validada: bool
