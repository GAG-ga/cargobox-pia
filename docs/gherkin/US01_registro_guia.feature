# language: es
@US01 @RN-01 @RN-02 @RN-03 @RN-20
Característica: Registro de envío y generación de guía
  Como empleado de sucursal
  Quiero registrar el peso, las dimensiones, el destino y el nivel de servicio de un paquete
  Para generar un código de guía único e imprimir la etiqueta

  Escenario: Paquete dentro de los límites genera guía estándar
    Dado un paquete de 10 kg con medidas 40 x 30 x 20 cm
    Y el origen con código postal "66450" y el destino con código postal "66220"
    Y el nivel de servicio "ESTANDAR"
    Cuando el empleado registra el envío
    Entonces el sistema genera una guía con formato "CBX-000000"
    Y la guía queda en estado "RECIBIDO"
    Y la tarifa es de $249.00
    Y la fecha estimada es 5 días hábiles después

  Esquema del escenario: Paquete que excede los límites es carga especial
    Dado un paquete de <peso> kg con medidas <medidas> cm
    Cuando el empleado intenta registrar el envío
    Entonces el sistema responde "CargaEspecialRequerida"
    Y no se genera ninguna guía

    Ejemplos:
      | peso  | medidas         |
      | 30.01 | 40 x 30 x 20    |
      | 10    | 101 x 50 x 50   |

  Escenario: Paquete exactamente en el límite se acepta
    Dado un paquete de 30 kg con medidas 100 x 100 x 100 cm
    Cuando el empleado registra el envío
    Entonces el sistema genera la guía

  Escenario: Tarifa Express nacional con peso volumétrico
    Dado un paquete de 2 kg con medidas 50 x 40 x 30 cm
    Y el origen con código postal "66450" y el destino con código postal "01000"
    Y el nivel de servicio "EXPRESS"
    Cuando el empleado registra el envío
    Entonces el kg cobrable es 12
    Y la tarifa es de $803.52
