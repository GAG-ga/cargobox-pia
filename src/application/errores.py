from src.domain.errores import ErrorDominio


class GuiaNoEncontrada(ErrorDominio):
    mensaje = "No encontramos ninguna guía con ese número. Revisa que esté bien escrito (CBX-000000)."


class IncidenciaNoEncontrada(ErrorDominio):
    mensaje = "No existe una incidencia con ese folio."


class AccesoDenegado(ErrorDominio):  # RN-08
    mensaje = ("Solo el remitente de la guía puede ver el historial completo. "
               "Verifica el teléfono registrado.")
