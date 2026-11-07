"""Publicador de Domain Events en memoria con suscriptores (ADR-004)."""
import logging
from collections import defaultdict

from src.domain import eventos as ev

log = logging.getLogger("cargobox.notificaciones")


class PublicadorEnMemoria:
    def __init__(self):
        self._suscriptores = defaultdict(list)

    def suscribir(self, tipo_evento, manejador):
        self._suscriptores[tipo_evento].append(manejador)

    def publicar(self, eventos: list) -> None:
        for evento in eventos:
            for manejador in self._suscriptores[type(evento)]:
                manejador(evento)


class NotificacionHandler:
    """Simula los avisos al remitente/destinatario (en producción: correo o SMS)."""

    def __init__(self):
        self.enviadas: list[str] = []

    def __call__(self, evento):
        texto = {
            ev.GuiaEnResguardo: "Aviso al destinatario: tu paquete está en resguardo; recógelo o reagenda.",
            ev.IntentoEntregaFallido: "Aviso al destinatario: intentamos entregar tu paquete.",
            ev.EntregaCompletada: "Aviso al remitente: tu paquete fue entregado.",
            ev.PerdidaDeclarada: "Aviso al remitente: tu paquete fue declarado perdido.",
        }.get(type(evento))
        if texto:
            mensaje = f"[{evento.referencia}] {texto}"
            self.enviadas.append(mensaje)
            log.info(mensaje)


def publicador_con_notificaciones() -> tuple[PublicadorEnMemoria, NotificacionHandler]:
    publicador, handler = PublicadorEnMemoria(), NotificacionHandler()
    for tipo in (ev.GuiaEnResguardo, ev.IntentoEntregaFallido, ev.EntregaCompletada,
                 ev.PerdidaDeclarada):
        publicador.suscribir(tipo, handler)
    return publicador, handler
