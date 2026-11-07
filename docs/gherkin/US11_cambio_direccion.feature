# language: es
@US11 @RN-14
Característica: Modificación de dirección en tránsito
  Como agente de atención al cliente
  Quiero actualizar la dirección de entrega de un paquete en tránsito previa validación de identidad
  Para redirigirlo con el cargo adicional calculado

  Escenario: Cambio de dirección con identidad validada
    Dado una guía en estado "EN_TRANSITO" con garantía de tiempo
    Cuando el agente valida la identidad del destinatario y cambia la dirección
    Entonces la guía tiene la nueva dirección
    Y se registra un cargo adicional de $80.00 para el destinatario
    Y la guía pierde la garantía de tiempo de entrega

  Escenario: Sin validación de identidad no hay cambio
    Dado una guía en estado "EN_TRANSITO"
    Cuando el agente intenta cambiar la dirección sin validar identidad
    Entonces el sistema responde "IdentidadNoValidada"

  Escenario: No se cambia la dirección de una guía en reparto
    Dado una guía en estado "EN_REPARTO"
    Cuando el agente intenta cambiar la dirección
    Entonces el sistema responde "CambioDireccionNoPermitido"
