# language: es
@US08 @RN-12 @RN-20
Característica: Consulta del estado de envío para destinatarios
  Como destinatario
  Quiero consultar mi número de guía en la página web
  Para ver el estado actual y la fecha estimada sin exponer datos internos

  Escenario: Consulta pública muestra solo estado y fecha estimada
    Dado una guía "CBX-000001" en estado "EN_TRANSITO" con 3 eventos de rastreo
    Cuando el destinatario consulta "CBX-000001"
    Entonces ve el estado "EN_TRANSITO" y la fecha estimada
    Y un mensaje entendible para el cliente
    Y no ve el historial de eventos ni ubicaciones internas

  Escenario: Guía inexistente
    Cuando el destinatario consulta "CBX-999999"
    Entonces el sistema responde "GuiaNoEncontrada" con un mensaje entendible
