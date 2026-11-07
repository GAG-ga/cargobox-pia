# ADR-002: La Guía es la raíz del agregado y dueña de su historial de rastreo

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-10-12, U3) · Ratificada en el PIA |
| **Contexto** | El criterio de éxito exige que el 100 % de los cambios de estado generen un evento de rastreo (RN-05, TR-02). |
| **Alternativas** | Tabla de eventos que cada módulo llena por su cuenta; triggers en la base de datos. |
| **Decisión** | `EventoRastreo`, `IntentoEntrega` y `EvidenciaEntrega` viven dentro del agregado `Guia`. Todo cambio de estado pasa por un único método privado (`_transicionar`) que consulta la máquina de estados (ADR-007) y registra el evento. Ningún servicio crea eventos ni cambia `estado` directamente. |
| **Consecuencias** | (+) Rastreo completo por diseño. (−) El agregado crece con el historial; las consultas lo leen desde el modelo de lectura (ADR-003). |
| **Trazabilidad** | US04–US07, US10, US15; RN-04, RN-05, RN-06, RN-07 |
