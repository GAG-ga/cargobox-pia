"""Value Objects: inmutables y siempre válidos (se validan al construirse)."""
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from src.domain.errores import DatoInvalido, EvidenciaIncompleta

PESO_MAXIMO_KG = Decimal("30")
LADO_MAXIMO_CM = Decimal("100")
DIVISOR_VOLUMETRICO = Decimal("5000")


@dataclass(frozen=True)
class NumeroGuia:
    """RN-02: código único impreso en la etiqueta."""

    valor: str

    def __post_init__(self):
        if not re.fullmatch(r"CBX-\d{6}", self.valor or ""):
            raise DatoInvalido("El número de guía debe tener el formato CBX-000000.")

    @classmethod
    def desde_secuencia(cls, n: int) -> "NumeroGuia":
        return cls(f"CBX-{n:06d}")

    def __str__(self):
        return self.valor


@dataclass(frozen=True)
class Dinero:
    """Montos en pesos mexicanos con 2 decimales."""

    monto: Decimal

    def __post_init__(self):
        valor = Decimal(str(self.monto)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if valor < 0:
            raise DatoInvalido("Un monto no puede ser negativo.")
        object.__setattr__(self, "monto", valor)

    @classmethod
    def cero(cls) -> "Dinero":
        return cls(Decimal("0"))

    def __add__(self, otro: "Dinero") -> "Dinero":
        return Dinero(self.monto + otro.monto)

    def por(self, factor) -> "Dinero":
        return Dinero(self.monto * Decimal(str(factor)))

    def minimo(self, otro: "Dinero") -> "Dinero":
        return self if self.monto <= otro.monto else otro


@dataclass(frozen=True)
class Peso:
    kg: Decimal

    def __post_init__(self):
        valor = Decimal(str(self.kg))
        if valor <= 0:
            raise DatoInvalido("El peso debe ser mayor que 0 kg.")
        object.__setattr__(self, "kg", valor)


@dataclass(frozen=True)
class Dimensiones:
    largo_cm: Decimal
    ancho_cm: Decimal
    alto_cm: Decimal

    def __post_init__(self):
        for campo in ("largo_cm", "ancho_cm", "alto_cm"):
            valor = Decimal(str(getattr(self, campo)))
            if valor <= 0:
                raise DatoInvalido("Las dimensiones deben ser mayores que 0 cm.")
            object.__setattr__(self, campo, valor)

    @property
    def lado_mayor(self) -> Decimal:
        return max(self.largo_cm, self.ancho_cm, self.alto_cm)

    @property
    def peso_volumetrico(self) -> Decimal:
        """RN-03: largo x ancho x alto / 5000."""
        return self.largo_cm * self.ancho_cm * self.alto_cm / DIVISOR_VOLUMETRICO


@dataclass(frozen=True)
class Paquete:
    """Lo que el remitente entrega en sucursal: peso + dimensiones."""

    peso: Peso
    dimensiones: Dimensiones

    @property
    def kg_cobrable(self) -> Decimal:
        """RN-03: el mayor entre peso real y volumétrico."""
        return max(self.peso.kg, self.dimensiones.peso_volumetrico)


@dataclass(frozen=True)
class Persona:
    nombre: str
    telefono: str

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise DatoInvalido("El nombre es obligatorio.")
        if not re.fullmatch(r"\d{10}", self.telefono or ""):
            raise DatoInvalido("El teléfono debe tener 10 dígitos.")


@dataclass(frozen=True)
class Direccion:
    calle: str
    codigo_postal: str

    def __post_init__(self):
        if not self.calle or not self.calle.strip():
            raise DatoInvalido("La calle es obligatoria.")
        if not re.fullmatch(r"\d{5}", self.codigo_postal or ""):
            raise DatoInvalido("El código postal debe tener 5 dígitos.")


@dataclass(frozen=True)
class EvidenciaEntrega:
    """RN-07 / RN-11: firma digital, foto y nombre de quien recibe."""

    firma_digital: str
    foto: str
    nombre_receptor: str
    es_tercero: bool = False

    def __post_init__(self):
        if not self.firma_digital or not self.foto or not (self.nombre_receptor or "").strip():
            raise EvidenciaIncompleta()


class NivelServicio(StrEnum):
    ESTANDAR = "ESTANDAR"
    EXPRESS = "EXPRESS"


class Zona(StrEnum):
    LOCAL = "LOCAL"
    REGIONAL = "REGIONAL"
    NACIONAL = "NACIONAL"

    @classmethod
    def entre(cls, origen: Direccion, destino: Direccion) -> "Zona":
        """RN-03: mismos 2 primeros dígitos del CP = local; mismo primero = regional."""
        if origen.codigo_postal[:2] == destino.codigo_postal[:2]:
            return cls.LOCAL
        if origen.codigo_postal[0] == destino.codigo_postal[0]:
            return cls.REGIONAL
        return cls.NACIONAL
