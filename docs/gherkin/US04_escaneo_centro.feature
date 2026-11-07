# language: es
@US04 @RN-04 @RN-05
Característica: Escaneo de ingreso y salida en centro de distribución
  Como personal del centro de distribución
  Quiero escanear la guía al recibir o despachar un paquete
  Para actualizar su ubicación y mantener la trazabilidad en tiempo real

  Escenario: Escaneo que avanza al siguiente estado registra un evento
    Dado una guía en estado "RECIBIDO"
    Cuando el personal escanea la guía en "CEDIS Monterrey" con estado "CLASIFICADO"
    Entonces la guía queda en estado "CLASIFICADO"
    Y se registra un evento de rastreo con ubicación "CEDIS Monterrey" y fecha/hora

  Escenario: Escaneo que salta un estado es rechazado
    Dado una guía en estado "RECIBIDO"
    Cuando el personal escanea la guía con estado "EN_TRANSITO"
    Entonces el sistema responde "TransicionEstadoInvalida"
    Y no se registra ningún evento nuevo
