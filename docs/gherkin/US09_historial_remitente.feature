# language: es
@US09 @RN-08 @RN-05
Característica: Consulta de historial detallado para remitentes
  Como remitente
  Quiero ver la línea de tiempo completa de los eventos de rastreo de mi paquete
  Para conocer cada punto de control y su hora exacta

  Escenario: El remitente ve todos los eventos en orden
    Dado una guía que pasó por "RECIBIDO", "CLASIFICADO" y "EN_TRANSITO"
    Cuando el remitente consulta su historial
    Entonces ve 3 eventos en orden cronológico con estado, ubicación y fecha/hora

  Escenario: Historial de una guía inexistente
    Cuando el remitente consulta el historial de "CBX-999999"
    Entonces el sistema responde "GuiaNoEncontrada" con un mensaje entendible

  Escenario: Otra persona no puede ver el historial
    Dado una guía cuyo remitente tiene el teléfono "8112345678"
    Cuando alguien consulta el historial con el teléfono "8100000000"
    Entonces el sistema responde "AccesoDenegado"
