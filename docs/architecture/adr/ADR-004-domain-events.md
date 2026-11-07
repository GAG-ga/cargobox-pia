# ADR-004: Domain Events para notificaciones

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-10-12, U3) · Ratificada en el PIA |
| **Contexto** | US05 y US10 piden notificar al destinatario; el remitente debe enterarse de la entrega. El dominio no debe depender de correos ni SMS. |
| **Alternativas** | Que cada Application Service llame directamente al notificador. |
| **Decisión** | Los agregados acumulan eventos (`GuiaGenerada`, `EstadoCambiado`, `IntentoEntregaFallido`, `GuiaEnResguardo`, `EntregaCompletada`, `AlertaGenerada`, `IncidenciaEscalada`, `PerdidaDeclarada`). Tras confirmar la transacción, el servicio los entrega a `PublicadorEventos`, que los despacha a los suscriptores (`NotificacionHandler`). |
| **Consecuencias** | (+) Nuevas reacciones sin tocar la Guía (abierto/cerrado). (−) Si la publicación falla después del commit, el evento se pierde; el patrón Outbox queda como evolución documentada. |
| **Trazabilidad** | US01, US05, US06, US10, US12, US13, US15; RN-05, RN-06 |
