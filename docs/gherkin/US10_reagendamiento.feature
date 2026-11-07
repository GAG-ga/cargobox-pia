# language: es
@US10 @RN-13
Característica: Reagendamiento tras intentos fallidos
  Como destinatario
  Quiero recoger en el centro de distribución o reagendar la visita
  Para evitar la devolución dentro de los 5 días hábiles de resguardo

  Antecedentes:
    Dado una guía en estado "EN_RESGUARDO" desde el lunes 2 de noviembre de 2026

  Escenario: Reagendar dentro del plazo
    Cuando el destinatario reagenda la visita el miércoles 4 de noviembre
    Entonces la guía vuelve a estado "EN_REPARTO"

  Escenario: Recoger en el centro dentro del plazo
    Cuando el destinatario recoge el paquete en el centro con firma y foto
    Entonces la guía queda en estado "ENTREGADO"

  Escenario: Vence el resguardo sin acción del destinatario
    Cuando se revisan los resguardos el martes 10 de noviembre
    Entonces la guía queda en estado "DEVUELTO"

  Escenario: El día 5 hábil todavía está dentro del plazo
    Cuando se revisan los resguardos el lunes 9 de noviembre
    Entonces la guía sigue en estado "EN_RESGUARDO"

  Escenario: Solo se permite un reagendamiento
    Dado que la guía ya se reagendó una vez y la visita falló
    Cuando el destinatario intenta reagendar de nuevo
    Entonces el sistema responde "ReagendamientoNoPermitido"
