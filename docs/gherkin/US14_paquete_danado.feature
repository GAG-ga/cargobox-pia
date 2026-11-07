# language: es
@US14 @RN-17
Característica: Apertura de folio por paquete dañado
  Como agente de atención al cliente
  Quiero registrar un folio de incidencia con evidencia fotográfica
  Para enviar la solicitud de reembolso o reposición al supervisor de la sucursal de origen

  Escenario: Folio con evidencia se asigna al supervisor de origen
    Dado una guía entregada generada en la sucursal "Sucursal San Nicolás"
    Cuando el agente abre un folio por daño con la foto "dano.jpg"
    Entonces se crea una incidencia "DANO" con folio
    Y queda asignada al supervisor de "Sucursal San Nicolás"

  Escenario: Folio sin foto no se registra
    Cuando el agente intenta abrir un folio por daño sin foto
    Entonces el sistema responde "EvidenciaIncompleta"

  Escenario: El supervisor resuelve con reembolso
    Dado un folio por daño abierto
    Cuando el supervisor decide "REEMBOLSO"
    Entonces la incidencia queda "RESUELTA" con la resolución "REEMBOLSO"
