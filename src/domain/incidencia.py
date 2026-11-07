"""Aggregate Root Incidencia: alertas por retraso (US12/US13) y folios por daño (US14)."""
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from src.domain import eventos as ev
from src.domain.errores import DatoInvalido, EvidenciaIncompleta, ResolucionInvalida

ATENCION_AL_CLIENTE = "Atención al Cliente"
SUPERVISOR_OPERACIONES = "Supervisor de operaciones"


class TipoIncidencia(StrEnum):
    RETRASO = "RETRASO"
    DANO = "DANO"


class EstadoIncidencia(StrEnum):
    ABIERTA = "ABIERTA"
    ESCALADA = "ESCALADA"
    RESUELTA = "RESUELTA"


class Resolucion(StrEnum):
    REEMBOLSO = "REEMBOLSO"
    REPOSICION = "REPOSICION"
    ATENDIDA = "ATENDIDA"


@dataclass(eq=False)
class Incidencia:
    folio: str
    numero_guia: str
    tipo: TipoIncidencia
    abierta_en: datetime
    asignada_a: str
    estado: EstadoIncidencia = EstadoIncidencia.ABIERTA
    evidencia_foto: str | None = None
    resolucion: Resolucion | None = None
    _eventos_dominio: list = field(default_factory=list, repr=False)

    def __post_init__(self):
        if not re.fullmatch(r"INC-\d{6}", self.folio):
            raise DatoInvalido("El folio debe tener el formato INC-000000.")

    @staticmethod
    def folio_desde_secuencia(n: int) -> str:
        return f"INC-{n:06d}"

    @classmethod
    def abrir_alerta_retraso(cls, folio, numero_guia, ahora) -> "Incidencia":
        """RN-15: alerta visible para operaciones; la atiende Atención al Cliente."""
        inc = cls(folio, numero_guia, TipoIncidencia.RETRASO, ahora, ATENCION_AL_CLIENTE)
        inc._eventos_dominio.append(ev.AlertaGenerada(folio, ahora, numero_guia))
        return inc

    @classmethod
    def abrir_folio_dano(cls, folio, numero_guia, foto, sucursal_origen, ahora) -> "Incidencia":
        """RN-17: requiere foto y se asigna al supervisor de la sucursal de origen."""
        if not foto:
            raise EvidenciaIncompleta("El folio por daño requiere evidencia fotográfica.")
        return cls(folio, numero_guia, TipoIncidencia.DANO, ahora,
                   f"Supervisor de {sucursal_origen}", evidencia_foto=foto)

    def escalar(self, ahora: datetime):
        """RN-16: se reasigna al supervisor de operaciones."""
        self.estado = EstadoIncidencia.ESCALADA
        self.asignada_a = SUPERVISOR_OPERACIONES
        self._eventos_dominio.append(ev.IncidenciaEscalada(self.folio, ahora, self.numero_guia))

    def resolver(self, resolucion: Resolucion):
        if self.estado == EstadoIncidencia.RESUELTA:
            raise ResolucionInvalida()
        validas = ({Resolucion.REEMBOLSO, Resolucion.REPOSICION}
                   if self.tipo == TipoIncidencia.DANO else {Resolucion.ATENDIDA})
        if resolucion not in validas:
            raise ResolucionInvalida()
        self.resolucion = resolucion
        self.estado = EstadoIncidencia.RESUELTA

    def extraer_eventos_dominio(self) -> list:
        pendientes, self._eventos_dominio = self._eventos_dominio, []
        return pendientes
