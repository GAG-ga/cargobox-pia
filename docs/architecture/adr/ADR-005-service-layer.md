# ADR-005: Service Layer delgada con Application Services por área del negocio

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-10-14, U3) · **Ampliada en el PIA** a las 15 historias |
| **Contexto** | Cada caso de uso debe coordinar repositorio, dominio, transacción y eventos sin contener reglas. En la U3 había 4 servicios para 5 historias; ahora son 15. |
| **Alternativas** | Un Handler por caso de uso (15 clases); un solo servicio con todo. |
| **Decisión** | Cinco servicios agrupados por actor/área, un método por caso de uso:<br>• `EnvioApplicationService`: registrar_guia (US01), cancelar (US02), corregir_destino (US03), cambiar_direccion (US11)<br>• `RastreoApplicationService`: registrar_escaneo (US04)<br>• `EntregaApplicationService`: registrar_intento_fallido (US05), capturar_evidencia_entrega (US06, US07), reagendar / recoger_en_centro (US10)<br>• `IncidenciaApplicationService`: monitorear_retrasos (US12), escalar_alertas (US13), abrir_folio_dano / resolver (US14), declarar_perdida (US15), vencer_resguardos (US10)<br>• `ConsultaRastreoQueryService`: estado_publico (US08), historial (US09) |
| **Consecuencias** | (+) Agrupa por actor y deja claro qué orquesta cada servicio. (−) `EnvioApplicationService` e `IncidenciaApplicationService` tienen 4–5 métodos; si crecen más se dividen. |
| **Trazabilidad** | US01–US15; Tabla 9 de la U3 |
