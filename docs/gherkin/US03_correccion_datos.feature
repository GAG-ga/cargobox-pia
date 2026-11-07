# language: es
@US03 @RN-10
Característica: Corrección de datos en sucursal
  Como empleado de sucursal
  Quiero modificar el origen o destino de un paquete no clasificado
  Para corregir errores de captura sin generar una nueva guía

  Escenario: Corregir el destino de una guía no clasificada
    Dado una guía "CBX-000001" en estado "RECIBIDO" con destino "Calle Roble 10, CP 66220"
    Cuando el empleado corrige el destino a "Calle Roble 12, CP 66220"
    Entonces la guía "CBX-000001" conserva su número
    Y su destino es "Calle Roble 12, CP 66220"

  Escenario: No se pueden corregir datos de una guía clasificada
    Dado una guía en estado "CLASIFICADO"
    Cuando el empleado intenta corregir el destino
    Entonces el sistema responde "CorreccionNoPermitida"
