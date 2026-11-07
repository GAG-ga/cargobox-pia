# ADR-011: Reglas de tiempo como casos de uso de monitoreo invocables

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-11-05, PIA) |
| **Contexto** | Cuatro reglas dependen del paso del tiempo y no de una acción de usuario: alerta a las 24 h (RN-15), escalamiento a las 48 h (RN-16), vencimiento del resguardo a los 5 días hábiles (RN-13) y pérdida a los 10 días (RN-18, que la declara un supervisor). |
| **Alternativas** | Hilos o scheduler dentro de la aplicación; triggers de base de datos; cola de mensajes. |
| **Decisión** | Cada regla de tiempo es un caso de uso de `IncidenciaApplicationService` que recibe `ahora` (puerto `Reloj`) y usa las Specifications para elegir candidatos. Se exponen en `POST /monitoreo/ejecutar`, que puede llamar un cron externo (Render Cron Job) o el presentador durante la demo con una fecha simulada. |
| **Consecuencias** | (+) Deterministas y probables (el tiempo se inyecta); la demo puede "adelantar el reloj". (−) Requiere un disparador externo en producción. |
| **Trazabilidad** | US10, US12, US13, US15; RN-13, RN-15, RN-16, RN-18 |
