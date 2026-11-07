# ADR-007: Máquina de estados explícita para el ciclo de vida de la guía

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-11-05, PIA) |
| **Contexto** | La guía tiene 10 estados (BRD §9.1) con transiciones permitidas, estados finales y excepciones (cancelación, resguardo, reagendamiento, devolución, pérdida). En la U3 solo se validaba el orden con `if`. |
| **Alternativas** | `if/elif` en cada método; patrón State con una clase por estado; librería externa (`transitions`). |
| **Decisión** | `MaquinaEstadosGuia` en `src/domain/estados.py`: una **tabla de transiciones** `{estado_origen: {estado_destino: nombre_de_la_accion}}` con los métodos `puede(origen, destino)`, `validar(origen, destino)` (lanza `TransicionEstadoInvalida`) y `es_final(estado)`. La Guía delega en ella dentro de `_transicionar`. Se prefirió la tabla al patrón State porque los estados no tienen comportamiento propio distinto, solo reglas de paso; y a una librería para no agregar dependencias al dominio. |
| **Consecuencias** | (+) El diagrama `docs/diagramas/03-maquina-estados` y el código son la misma tabla; agregar un estado es agregar una fila. La tabla se prueba completa (cada par permitido y prohibido). (−) Las condiciones extra de una transición (p. ej. 2 intentos, 5 días) siguen en la Guía / Specifications, no en la tabla. |
| **Trazabilidad** | RN-04, RN-05, RN-06, RN-09, RN-13, RN-18; US02, US04–US07, US10, US15 |
