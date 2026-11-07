# language: es
@US12 @RN-15
Característica: Generación automática de alerta por retraso
  Como supervisor de operaciones
  Quiero recibir una alerta si un paquete pasa 24 horas sin actualizar su estado
  Para detectar anomalías de forma preventiva

  Escenario: 24 horas sin cambio genera alerta
    Dado una guía en estado "EN_TRANSITO" cuyo último evento fue hace 24 horas
    Cuando se ejecuta el monitoreo de retrasos
    Entonces se abre una alerta por retraso para esa guía

  Escenario: 23 horas sin cambio no genera alerta
    Dado una guía en estado "EN_TRANSITO" cuyo último evento fue hace 23 horas
    Cuando se ejecuta el monitoreo de retrasos
    Entonces no se abre ninguna alerta

  Escenario: Las guías en estado final no generan alerta
    Dado una guía en estado "ENTREGADO" cuyo último evento fue hace 72 horas
    Cuando se ejecuta el monitoreo de retrasos
    Entonces no se abre ninguna alerta

  Escenario: No se duplica la alerta
    Dado una guía que ya tiene una alerta abierta
    Cuando se ejecuta el monitoreo de retrasos otra vez
    Entonces sigue existiendo una sola alerta abierta
