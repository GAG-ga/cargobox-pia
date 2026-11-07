"""Errores de dominio con nombres del glosario. Cada uno lleva un mensaje para el cliente."""


class ErrorDominio(Exception):
    """Base de los errores de negocio. `mensaje` es lo que verá el usuario."""

    mensaje = "La operación no está permitida por las reglas de CargoBox."

    def __init__(self, detalle: str | None = None):
        self.detalle = detalle
        super().__init__(detalle or self.mensaje)


class DatoInvalido(ErrorDominio):
    mensaje = "Alguno de los datos enviados no es válido."


class CargaEspecialRequerida(ErrorDominio):  # RN-01
    mensaje = ("El paquete excede 30 kg o 100 cm por lado: debe enviarse como carga especial "
               "y no puede recibir una guía estándar.")


class TransicionEstadoInvalida(ErrorDominio):  # RN-04
    mensaje = "La guía no puede pasar a ese estado: debe seguir el orden del recorrido."


class LimiteIntentosExcedido(ErrorDominio):  # RN-06
    mensaje = ("Ya se realizaron los 2 intentos de entrega. El paquete está en resguardo: "
               "el destinatario puede recogerlo o reagendar.")


class EvidenciaIncompleta(ErrorDominio):  # RN-07, RN-11, RN-17
    mensaje = "Falta evidencia: se requiere firma digital, foto y el nombre de quien recibe."


class EntregaYaRegistrada(ErrorDominio):  # RN-07
    mensaje = "Esta guía ya fue entregada; no se puede registrar otra entrega."


class CancelacionNoPermitida(ErrorDominio):  # RN-09
    mensaje = ("La guía ya fue clasificada y no se puede cancelar. Solo se permite cambiar "
               "la dirección de entrega.")


class CorreccionNoPermitida(ErrorDominio):  # RN-10
    mensaje = "La guía ya fue clasificada: sus datos ya no se pueden corregir en sucursal."


class ReagendamientoNoPermitido(ErrorDominio):  # RN-13
    mensaje = ("No se puede reagendar: la guía no está en resguardo, ya se reagendó una vez "
               "o venció el plazo de 5 días hábiles.")


class CambioDireccionNoPermitido(ErrorDominio):  # RN-14
    mensaje = ("Solo se puede cambiar la dirección mientras el paquete está en tránsito o en "
               "el centro destino.")


class IdentidadNoValidada(ErrorDominio):  # RN-14
    mensaje = "Para cambiar la dirección primero se debe validar la identidad del destinatario."


class PerdidaNoDeclarable(ErrorDominio):  # RN-18
    mensaje = ("La guía no puede declararse perdida: debe estar en ruta y llevar más de "
               "10 días naturales sin actualización.")


class ResolucionInvalida(ErrorDominio):  # RN-17
    mensaje = "La resolución no es válida para este tipo de incidencia o ya fue resuelta."


class OperacionNoProcesable(ErrorDominio):  # Paquete docente: puede_procesarse
    mensaje = ("La operación no puede procesarse: el remitente debe estar activo, la operación debe "
               "tener al menos un servicio, estar autorizada y los servicios deben tener capacidad.")
