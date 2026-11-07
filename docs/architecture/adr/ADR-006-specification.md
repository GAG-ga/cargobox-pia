# ADR-006: Patrón Specification para las condiciones de negocio

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-11-05, PIA) |
| **Contexto** | Varias reglas son **condiciones** sobre una guía o incidencia que se reutilizan en distintos lugares: ¿cumple los límites? (RN-01), ¿se puede cancelar? (RN-09), ¿se puede corregir? (RN-10), ¿admite cambio de dirección? (RN-14), ¿necesita alerta? (RN-15), ¿se escala? (RN-16), ¿se puede declarar perdida? (RN-18), ¿venció el resguardo? (RN-13), ¿el Express llegó tarde? (RN-19). Si se escriben como `if` sueltos, la misma condición aparece en el dominio, en el monitoreo y en las consultas, y es fácil que diverjan. |
| **Alternativas** | `if` dentro de cada método; métodos booleanos sueltos en la Guía; reglas en la base de datos (consultas SQL). |
| **Decisión** | Clase base `Specification` con `es_satisfecha_por(candidato)` y combinadores `&`, `\|`, `~`. Cada regla condicional es una clase con nombre del negocio en `src/domain/especificaciones.py` (`CumpleLimitesEstandar`, `PuedeCancelarse`, `PermiteCorreccion`, `PermiteCambioDireccion`, `RequiereAlertaPorRetraso`, `DebeEscalarse`, `PuedeDeclararsePerdida`, `ResguardoVencido`, `ExpressFueraDeTiempo`). La Guía las usa para proteger sus métodos y el `IncidenciaApplicationService` las usa para filtrar candidatos en el monitoreo. |
| **Consecuencias** | (+) Una regla = una clase con nombre del glosario, probable de forma aislada y reutilizable; nuevas reglas se agregan sin modificar las existentes (abierto/cerrado). (−) Más clases pequeñas; las especificaciones con tiempo reciben `ahora` explícito para ser deterministas. |
| **Trazabilidad** | RN-01, RN-09, RN-10, RN-13, RN-14, RN-15, RN-16, RN-18, RN-19; US01, US02, US03, US10–US15 |
