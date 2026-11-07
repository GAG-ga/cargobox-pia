# language: es
@US05 @RN-06
Característica: Registro de intento de entrega fallido
  Como repartidor
  Quiero registrar que el destinatario no se encontraba en el domicilio
  Para notificar la visita y programar el siguiente intento

  Antecedentes:
    Dado una guía en estado "EN_REPARTO"

  Escenario: Primer intento fallido
    Cuando el repartidor registra un intento fallido por "destinatario ausente"
    Entonces la guía tiene 1 intento fallido
    Y la guía sigue en estado "EN_REPARTO"

  Escenario: Segundo intento fallido envía la guía a resguardo
    Dado que ya tiene 1 intento fallido
    Cuando el repartidor registra otro intento fallido
    Entonces la guía queda en estado "EN_RESGUARDO"
    Y se notifica al destinatario para recoger o reagendar

  Escenario: Un tercer intento es rechazado
    Dado que la guía ya está en "EN_RESGUARDO" con 2 intentos fallidos
    Cuando el repartidor intenta registrar otro intento fallido
    Entonces el sistema responde "LimiteIntentosExcedido"
