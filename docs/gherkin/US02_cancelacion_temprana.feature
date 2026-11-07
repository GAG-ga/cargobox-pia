# language: es
@US02 @RN-09
Característica: Cancelación temprana de envío
  Como empleado de sucursal
  Quiero cancelar una guía recién creada antes de su clasificación
  Para anular envíos a solicitud del cliente mientras el paquete sigue en la sucursal

  Escenario: Cancelar una guía en estado RECIBIDO
    Dado una guía en estado "RECIBIDO"
    Cuando el empleado de sucursal la cancela
    Entonces la guía queda en estado "CANCELADO"
    Y se registra un evento de rastreo "CANCELADO"

  Escenario: No se puede cancelar una guía ya clasificada
    Dado una guía en estado "CLASIFICADO"
    Cuando el empleado de sucursal intenta cancelarla
    Entonces el sistema responde "CancelacionNoPermitida"
    Y la guía sigue en estado "CLASIFICADO"
