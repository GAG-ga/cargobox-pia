# language: es
@US07 @RN-11 @RN-07
Característica: Registro de entrega a terceros
  Como repartidor
  Quiero registrar el nombre y la firma de un tercero que recibe el paquete
  Para completar la entrega cuando el destinatario no está disponible

  Escenario: Entrega a un vecino
    Dado una guía en estado "EN_REPARTO"
    Cuando el repartidor registra la entrega al tercero "Luis Pérez (vecino)" con firma y foto
    Entonces la guía queda en estado "ENTREGADO"
    Y la evidencia indica que la recibió un tercero

  Escenario: Entrega a tercero sin nombre no se permite
    Dado una guía en estado "EN_REPARTO"
    Cuando el repartidor intenta registrar la entrega a un tercero sin nombre
    Entonces el sistema responde "EvidenciaIncompleta"
