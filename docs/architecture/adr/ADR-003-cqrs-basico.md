# ADR-003: CQRS básico — comandos y consultas separados

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-10-12, U3) · **Modificada en el PIA (2026-11-05)**: motor PostgreSQL (ADR-008) y lectura directa de la tabla de eventos |
| **Contexto** | US08 (destinatario) y US09 (remitente) solo leen; reducir llamadas a Atención al Cliente (TR-01) depende de que sean completas y rápidas. Además muestran información distinta (RN-08 vs RN-12). |
| **Alternativas** | Un solo servicio con lectura y escritura sobre el agregado; bases de datos separadas; proyección asíncrona (diseño U3). |
| **Decisión** | Los comandos los atienden los Application Services. Las consultas las atiende `ConsultaRastreoQueryService`, que usa la interfaz `HistorialRastreoReader` y devuelve vistas planas (`EstadoPublicoView` para US08, `HistorialEnvioView` para US09) **sin cargar el agregado**. En el PIA el lector consulta directamente las tablas `guias` y `eventos_rastreo` en la misma transacción de lectura, en lugar de una proyección asíncrona. |
| **Consecuencias** | (+) Las vistas de lectura no contaminan el dominio; se elimina la consistencia eventual y la necesidad de mantener una proyección. (−) Si el volumen creciera, habría que volver a una proyección (queda como evolución). |
| **Trazabilidad** | US08, US09; RN-08, RN-12; TR-01 |
