"""Mensajes entendibles para el cliente según el estado de la guía."""
from src.domain.estados import EstadoGuia as E

MENSAJES = {
    E.RECIBIDO: "Recibimos tu paquete en sucursal y pronto saldrá a su destino.",
    E.CLASIFICADO: "Tu paquete fue clasificado en nuestro centro de distribución.",
    E.EN_TRANSITO: "Tu paquete va en camino hacia la ciudad de destino.",
    E.CENTRO_DESTINO: "Tu paquete llegó al centro de distribución de tu ciudad.",
    E.EN_REPARTO: "Tu paquete salió a reparto y llegará hoy.",
    E.ENTREGADO: "Tu paquete fue entregado. ¡Gracias por usar CargoBox!",
    E.EN_RESGUARDO: ("No pudimos entregar tu paquete. Está en resguardo: puedes recogerlo en el "
                     "centro o reagendar la visita dentro de 5 días hábiles."),
    E.DEVUELTO: "El plazo de resguardo venció y el paquete regresa al remitente.",
    E.CANCELADO: "Este envío fue cancelado en sucursal.",
    E.PERDIDO: ("Lamentamos informarte que el paquete fue declarado perdido. "
                "El remitente recibirá la compensación correspondiente."),
}


def mensaje_para(estado: E) -> str:
    return MENSAJES[estado]
