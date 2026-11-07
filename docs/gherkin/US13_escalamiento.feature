# language: es
@US13 @RN-16
Característica: Escalamiento automático de incidencias
  Como supervisor de operaciones
  Quiero que las alertas sin resolver por 48 horas se me reasignen automáticamente
  Para intervenir en los casos críticos

  Escenario: Alerta con 48 horas se escala
    Dado una alerta abierta hace 48 horas
    Cuando se ejecuta el monitoreo de escalamiento
    Entonces la alerta queda "ESCALADA" y asignada al supervisor de operaciones

  Escenario: Alerta con 47 horas no se escala
    Dado una alerta abierta hace 47 horas
    Cuando se ejecuta el monitoreo de escalamiento
    Entonces la alerta sigue "ABIERTA"
