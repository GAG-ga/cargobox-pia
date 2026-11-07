"""Aggregate Root Guia (ADR-002): dueña de sus eventos, intentos y evidencia."""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal

from src.domain import eventos as ev
from src.domain.calendario import sumar_dias_habiles
from src.domain.errores import (
    CambioDireccionNoPermitido,
    CancelacionNoPermitida,
    CargaEspecialRequerida,
    CorreccionNoPermitida,
    EntregaYaRegistrada,
    IdentidadNoValidada,
    LimiteIntentosExcedido,
    PerdidaNoDeclarable,
    ReagendamientoNoPermitido,
    TransicionEstadoInvalida,
)
from src.domain.especificaciones import (
    CumpleLimitesEstandar,
    ExpressFueraDeTiempo,
    PermiteCambioDireccion,
    PermiteCorreccion,
    PuedeCancelarse,
    PuedeDeclararsePerdida,
    ResguardoVencido,
)
from src.domain.estados import EstadoGuia, MaquinaEstadosGuia
from src.domain.value_objects import (
    Dinero,
    Direccion,
    EvidenciaEntrega,
    NivelServicio,
    NumeroGuia,
    Paquete,
    Persona,
)

E = EstadoGuia
MAXIMO_INTENTOS = 2
CARGO_CAMBIO_DIRECCION = Dinero(Decimal("80"))
TOPE_COMPENSACION = Dinero(Decimal("5000"))
PORCENTAJE_REEMBOLSO_EXPRESS = Decimal("0.5")
ESCANEOS_DE_RUTA = {E.CLASIFICADO, E.EN_TRANSITO, E.CENTRO_DESTINO, E.EN_REPARTO}


@dataclass(frozen=True)
class EventoRastreo:
    estado: EstadoGuia
    ubicacion: str
    fecha_hora: datetime


@dataclass(frozen=True)
class IntentoEntrega:
    numero: int
    exitoso: bool
    fecha_hora: datetime
    motivo: str = ""


def calcular_fecha_estimada(nivel: NivelServicio, creada_en: datetime) -> date:
    """RN-20: Estándar 5 días hábiles; Express 48 h."""
    if nivel == NivelServicio.EXPRESS:
        return (creada_en + timedelta(hours=48)).date()
    return sumar_dias_habiles(creada_en.date(), 5)


@dataclass(eq=False)
class Guia:
    numero: NumeroGuia
    remitente: Persona
    destinatario: Persona
    origen: Direccion
    destino: Direccion
    paquete: Paquete
    nivel: NivelServicio
    valor_declarado: Dinero
    tarifa: Dinero
    sucursal_origen: str
    creada_en: datetime
    fecha_estimada: date
    estado: EstadoGuia = E.RECIBIDO
    eventos: list[EventoRastreo] = field(default_factory=list)
    intentos: list[IntentoEntrega] = field(default_factory=list)
    evidencia: EvidenciaEntrega | None = None
    con_garantia: bool = True
    reagendada: bool = False
    resguardo_desde: datetime | None = None
    cargos_adicionales: Dinero = field(default_factory=Dinero.cero)
    reembolso: Dinero = field(default_factory=Dinero.cero)
    compensacion: Dinero = field(default_factory=Dinero.cero)
    _eventos_dominio: list = field(default_factory=list, repr=False)

    # ------------------------------------------------------------------ US01
    @classmethod
    def generar(cls, numero, remitente, destinatario, origen, destino, paquete, nivel,
                valor_declarado, tarifa, sucursal_origen, ahora) -> "Guia":
        if not CumpleLimitesEstandar().es_satisfecha_por(paquete):  # RN-01
            raise CargaEspecialRequerida()
        guia = cls(numero, remitente, destinatario, origen, destino, paquete, nivel,
                   valor_declarado, tarifa, sucursal_origen, ahora,
                   calcular_fecha_estimada(nivel, ahora))
        guia._registrar_evento(E.RECIBIDO, sucursal_origen, ahora)  # RN-05
        guia._eventos_dominio.append(ev.GuiaGenerada(numero.valor, ahora))
        return guia

    # ------------------------------------------------------- núcleo RN-04/05
    def _transicionar(self, destino: EstadoGuia, ubicacion: str, ahora: datetime):
        """Único punto donde cambia el estado: valida con la máquina y deja evento."""
        MaquinaEstadosGuia.validar(self.estado, destino)
        self.estado = destino
        self._registrar_evento(destino, ubicacion, ahora)

    def _registrar_evento(self, estado, ubicacion, ahora):
        self.eventos.append(EventoRastreo(estado, ubicacion, ahora))
        self._eventos_dominio.append(ev.EstadoCambiado(self.numero.valor, ahora, estado.value))

    @property
    def ultima_actualizacion(self) -> datetime:
        return self.eventos[-1].fecha_hora

    @property
    def intentos_fallidos(self) -> int:
        return sum(1 for i in self.intentos if not i.exitoso)

    def extraer_eventos_dominio(self) -> list:
        pendientes, self._eventos_dominio = self._eventos_dominio, []
        return pendientes

    # ------------------------------------------------------------------ US04
    def registrar_escaneo(self, nuevo_estado: EstadoGuia, ubicacion: str, ahora: datetime):
        if nuevo_estado not in ESCANEOS_DE_RUTA:
            raise TransicionEstadoInvalida("Un escaneo solo mueve la guía por su ruta.")
        self._transicionar(nuevo_estado, ubicacion, ahora)

    # ------------------------------------------------------------------ US05
    def registrar_intento_fallido(self, motivo: str, ubicacion: str, ahora: datetime):
        if self.estado == E.EN_RESGUARDO:
            raise LimiteIntentosExcedido()
        if self.estado != E.EN_REPARTO:
            raise TransicionEstadoInvalida("Solo se registran intentos de una guía en reparto.")
        numero = len(self.intentos) + 1
        self.intentos.append(IntentoEntrega(numero, False, ahora, motivo))
        self._eventos_dominio.append(ev.IntentoEntregaFallido(self.numero.valor, ahora, numero))
        if self.intentos_fallidos >= MAXIMO_INTENTOS:  # RN-06 (y visita reagendada fallida)
            self._transicionar(E.EN_RESGUARDO, ubicacion, ahora)
            self.resguardo_desde = ahora
            self._eventos_dominio.append(ev.GuiaEnResguardo(self.numero.valor, ahora))

    # ------------------------------------------------------- US06, US07, US10
    def registrar_entrega(self, evidencia: EvidenciaEntrega, ubicacion: str, ahora: datetime):
        if self.estado == E.ENTREGADO:
            raise EntregaYaRegistrada()
        self._transicionar(E.ENTREGADO, ubicacion, ahora)
        self.intentos.append(IntentoEntrega(len(self.intentos) + 1, True, ahora))
        self.evidencia = evidencia
        if ExpressFueraDeTiempo(ahora).es_satisfecha_por(self):  # RN-19
            self.reembolso = self.tarifa.por(PORCENTAJE_REEMBOLSO_EXPRESS)
        self._eventos_dominio.append(ev.EntregaCompletada(self.numero.valor, ahora))

    # ------------------------------------------------------------------ US02
    def cancelar(self, ahora: datetime):
        if not PuedeCancelarse().es_satisfecha_por(self):  # RN-09
            raise CancelacionNoPermitida()
        self._transicionar(E.CANCELADO, self.sucursal_origen, ahora)

    # ------------------------------------------------------------------ US03
    def corregir_datos(self, origen: Direccion | None = None, destino: Direccion | None = None):
        if not PermiteCorreccion().es_satisfecha_por(self):  # RN-10
            raise CorreccionNoPermitida()
        self.origen = origen or self.origen
        self.destino = destino or self.destino

    # ------------------------------------------------------------------ US11
    def cambiar_direccion(self, nueva: Direccion, identidad_validada: bool, ahora: datetime):
        if not identidad_validada:
            raise IdentidadNoValidada()
        if not PermiteCambioDireccion().es_satisfecha_por(self):  # RN-14
            raise CambioDireccionNoPermitido()
        self.destino = nueva
        self.cargos_adicionales = self.cargos_adicionales + CARGO_CAMBIO_DIRECCION
        self.con_garantia = False
        self._eventos_dominio.append(ev.DireccionCambiada(self.numero.valor, ahora))

    # ------------------------------------------------------------------ US10
    def reagendar(self, ahora: datetime):
        if (self.estado != E.EN_RESGUARDO or self.reagendada
                or ResguardoVencido(ahora).es_satisfecha_por(self)):  # RN-13
            raise ReagendamientoNoPermitido()
        self.reagendada = True
        self.resguardo_desde = None
        self._transicionar(E.EN_REPARTO, "Reagendado por el destinatario", ahora)

    def devolver(self, ahora: datetime):
        if not ResguardoVencido(ahora).es_satisfecha_por(self):
            raise TransicionEstadoInvalida("El resguardo todavía no vence.")
        self._transicionar(E.DEVUELTO, "Devolución al remitente", ahora)

    # ------------------------------------------------------------------ US15
    def declarar_perdida(self, ahora: datetime):
        if not PuedeDeclararsePerdida(ahora).es_satisfecha_por(self):  # RN-18
            raise PerdidaNoDeclarable()
        self.compensacion = self.valor_declarado.minimo(TOPE_COMPENSACION)
        self._transicionar(E.PERDIDO, "Declaración de pérdida", ahora)
        self._eventos_dominio.append(
            ev.PerdidaDeclarada(self.numero.valor, ahora, str(self.compensacion.monto)))
