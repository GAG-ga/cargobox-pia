# Matriz de trazabilidad — CargoBox

Conecta cada necesidad del negocio (BRD §5) con su historia de usuario, sus reglas (BRD §9), el escenario Gherkin, la actividad del BPMN el código, las pruebas y el endpoint de la API que la implementan.

| Necesidad | Historia | Reglas | Gherkin | Actividad del BPMN | Código (`src/`) | Pruebas (`tests/aceptacion`, `tests/unit`) | Endpoint (API) |
|---|---|---|---|---|---|---|---|
| BRD §6 límites y tarifa | US01 Registro de guía | RN-01, RN-02, RN-03, RN-20 | `US01_registro_guia.feature` | Pesar, medir y cotizar → ¿≤ 30 kg y ≤ 100 cm? → Generar guía | `EnvioApplicationService.registrar_guia` · `Guia.generar` · `CumpleLimitesEstandar` · `Cotizador` | `test_us01_registro_guia.py` · `test_cotizador_y_calendario.py` | `POST /guias` |
| TR-03 | US02 Cancelación temprana | RN-09 | `US02_cancelacion_temprana.feature` | ¿Cliente cancela antes de clasificar? → Fin CANCELADO | `EnvioApplicationService.cancelar` · `Guia.cancelar` · `PuedeCancelarse` | `test_us02_cancelacion_temprana.py` · `tests/api/test_api_equipo.py` | `POST /guias/{n}/cancelacion` |
| TR-03 | US03 Corrección de datos | RN-10 | `US03_correccion_datos.feature` | Sucursal (antes de clasificación) | `EnvioApplicationService.corregir_datos` · `Guia.corregir_datos` · `PermiteCorreccion` | `test_us03_correccion_datos.py` | `PATCH /guias/{n}/datos` |
| TR-02 | US04 Escaneo en centro | RN-04, RN-05 | `US04_escaneo_centro.feature` | Escaneo de ingreso → Despacho → Centro destino → Salida a ruta | `RastreoApplicationService.registrar_escaneo` · `Guia.registrar_escaneo` · `MaquinaEstadosGuia` | `test_us04_escaneo_centro.py` · `test_maquina_estados.py` | `POST /guias/{n}/escaneos` |
| BRD §6 intentos | US05 Intento fallido | RN-06 | `US05_intento_fallido.feature` | Registrar intento fallido → ¿Es el 2º intento? → Resguardo | `EntregaApplicationService.registrar_intento_fallido` · `Guia.registrar_intento_fallido` | `test_us05_intento_fallido.py` | `POST /guias/{n}/intentos-fallidos` |
| TR-04 | US06 Evidencia de entrega | RN-07, RN-19 | `US06_evidencia_entrega.feature` | Capturar firma + foto → Fin ENTREGADO | `EntregaApplicationService.capturar_evidencia_entrega` · `Guia.registrar_entrega` · `ExpressFueraDeTiempo` | `test_us06_evidencia_entrega.py` | `POST /guias/{n}/entrega` |
| TR-04 | US07 Entrega a tercero | RN-11, RN-07 | `US07_entrega_tercero.feature` | ¿Destinatario o tercero presente? → Capturar firma + foto | `capturar_evidencia_entrega` (es_tercero) · `EvidenciaEntrega` | `test_us07_entrega_tercero.py` | `POST /guias/{n}/entrega` (es_tercero) |
| TR-01 | US08 Consulta destinatario | RN-12, RN-20 | `US08_consulta_destinatario.feature` | Consulta de estado (fuera de carriles) | `ConsultaRastreoQueryService.estado_publico` · `mensajes.py` | `test_us08_consulta_destinatario.py` · `tests/api/test_api_equipo.py` | `GET /rastreo/{n}` |
| TR-01 | US09 Historial remitente | RN-08, RN-05 | `US09_historial_remitente.feature` | Consulta de estado (fuera de carriles) | `ConsultaRastreoQueryService.historial` · `AccesoDenegado` | `test_us09_historial_remitente.py` | `GET /rastreo/{n}/historial` |
| BRD §6 resguardo | US10 Reagendamiento | RN-13 | `US10_reagendamiento.feature` | Resguardo → ¿Reagenda o recoge? → Fin DEVUELTO | `EntregaApplicationService.reagendar` · `IncidenciaApplicationService.vencer_resguardos` · `ResguardoVencido` | `test_us10_reagendamiento.py` | `POST /guias/{n}/reagendamiento` · `POST /monitoreo/ejecutar` |
| TR-03 | US11 Cambio de dirección | RN-14 | `US11_cambio_direccion.feature` | Cambio de dirección en tránsito (+$80, sin garantía) | `EnvioApplicationService.cambiar_direccion` · `Guia.cambiar_direccion` · `PermiteCambioDireccion` | `test_us11_cambio_direccion.py` | `PATCH /guias/{n}/direccion` |
| TR-05 | US12 Alerta por retraso | RN-15 | `US12_alerta_retraso.feature` | Timer 24 h → Generar alerta | `IncidenciaApplicationService.monitorear_retrasos` · `RequiereAlertaPorRetraso` | `test_us12_alerta_retraso.py` · `tests/api/test_api.py` | `POST /monitoreo/ejecutar` · `GET /incidencias` |
| TR-05 | US13 Escalamiento | RN-16 | `US13_escalamiento.feature` | Timer 48 h → Escalar a supervisor | `IncidenciaApplicationService.escalar_alertas` · `DebeEscalarse` · `Incidencia.escalar` | `test_us13_escalamiento.py` | `POST /monitoreo/ejecutar` · `GET /incidencias` |
| TR-03 | US14 Paquete dañado | RN-17 | `US14_paquete_danado.feature` | Atención al Cliente → folio de incidencia | `IncidenciaApplicationService.abrir_folio_dano` / `resolver` · `Incidencia` | `test_us14_paquete_danado.py` · `test_incidencia.py` | `POST /incidencias/danos` · `POST /incidencias/{folio}/resolucion` |
| TR-03 | US15 Declaración de pérdida | RN-18 | `US15_declaracion_perdida.feature` | Timer > 10 días → Declarar pérdida y compensar | `IncidenciaApplicationService.declarar_perdida` · `Guia.declarar_perdida` · `PuedeDeclararsePerdida` | `test_us15_declaracion_perdida.py` | `POST /guias/{n}/perdida` |

## Paquete de datos del docente

| Regla del paquete | Componente | Prueba | Evidencia |
|---|---|---|---|
| `puede_procesarse` (activo AND línea AND autorización) | `PuedeProcesarse` en `domain/operacion_servicio.py` | `test_puede_procesarse_and` | `paquete-docente/casos_prueba_resultados.csv` (CAR-T001…T060) |
| `beneficio_referencia` (preferente AND total ≥ 1500 AND NOT promoción) | `BeneficioReferencia` | `test_beneficio_referencia_and_not` | CAR-B001…B060 |
| Capacidad / disponibilidad | `ServiciosConCapacidad` | `test_servicios_con_capacidad` | CAR-S005, S015, S020 |
| Transiciones válidas e inválidas (RN-04, RN-09) | `MaquinaEstadosGuia` vía `OperacionServicio` | `test_saltar_estado_y_repetir_aprobacion_son_invalidos` | `paquete-docente/transiciones_prueba_resultados.csv` |

Diferencias con el BRD: [`paquete-docente.md`](paquete-docente.md).

## Cobertura de reglas

`tests/aceptacion/test_trazabilidad.py` verifica automáticamente que cada archivo `.feature` tenga su módulo de pruebas con al menos tantas pruebas como escenarios.

Las 20 reglas tienen al menos una historia y un escenario Gherkin. Las 15 historias tienen al menos un escenario de éxito y uno de error o límite.

## Hallazgos de la Unidad 3 resueltos en el PIA

| ID | Hallazgo | Resolución |
|---|---|---|
| H-01 | El BPMN no mostraba el segundo intento de entrega. | `diagramas/01-bpmn-proceso` incluye la compuerta «¿Es el 2º intento?» con regreso a ruta en el primer fallo. |
| H-02 | La imagen del modelo de dominio de la U2 era de otro caso (Pasajero, Conductor, Viaje). | Reemplazada por `diagramas/02-modelo-dominio`. |
| H-03 | Remitente, Destinatario, Evidencia y NivelServicio eran entidades en la U2. | Se modelan como Value Objects / enumeraciones (sin ciclo de vida propio). |
