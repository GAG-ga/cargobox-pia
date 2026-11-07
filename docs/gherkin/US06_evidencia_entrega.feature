# language: es
@US06 @RN-07 @RN-19
Característica: Captura de evidencia de entrega
  Como repartidor
  Quiero capturar la firma digital del receptor y una foto del paquete
  Para certificar la recepción exitosa del envío

  Escenario: Entrega con firma y foto
    Dado una guía en estado "EN_REPARTO"
    Cuando el repartidor captura firma "firma.png", foto "foto.jpg" y receptor "Ana López"
    Entonces la guía queda en estado "ENTREGADO"
    Y la evidencia queda asociada a la guía

  Escenario: Entrega sin foto no se permite
    Dado una guía en estado "EN_REPARTO"
    Cuando el repartidor intenta cerrar la entrega sin foto
    Entonces el sistema responde "EvidenciaIncompleta"
    Y la guía sigue en estado "EN_REPARTO"

  Escenario: Express entregado tarde genera reembolso del 50 %
    Dado una guía Express con tarifa de $400.00 generada hace 60 horas
    Cuando el repartidor registra la entrega con evidencia completa
    Entonces la guía tiene un reembolso de $200.00
