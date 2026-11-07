# BRD — CargoBox, Plataforma de Envíos Nacionales (Caso 14)

**Equipo:** Steven Roel Mejia Contreras (2226582) · Juan José Montoya Zapata (2226584) · Ivonne Niño Pérez (2222984)
**Curso:** Componentes de Lógica de Negocios — Prof. Miguel Ángel Gómez Marroquín
**Versión:** 2.0 (PIA) — refinamiento del BRD de la Unidad 2 (v1.0, 03/09/2026)

> **Qué cambió respecto a la v1.0 (U2):** se resolvieron los 3 pendientes de la sección 6.3 del Modelo de Dominio, se agregó el catálogo numerado de reglas de negocio (RN-01 a RN-20) para la trazabilidad con el código y las pruebas, y se completó el ciclo de estados del paquete (resguardo, devolución, cancelación y pérdida). Ver la [sección 11](#11-historial-de-cambios).

---

## 1. Contexto del negocio

CargoBox es una empresa de paquetería que ofrece envíos nacionales. El precio de cada envío depende de las dimensiones, el peso, el destino y el nivel de servicio contratado. Cada paquete recibido genera una **guía única** que lo identifica durante todo su recorrido.

El proceso inicia cuando el remitente entrega el paquete en una sucursal, donde se pesa, se mide y se genera la guía. Después avanza por los centros de distribución con los estados **recibido → clasificado → en tránsito → centro destino → en reparto → entregado**. Cada cambio de estado produce un evento de rastreo y la entrega final requiere evidencia de recepción.

## 2. Problema / Oportunidad

- Los clientes llaman con frecuencia a Atención al Cliente por falta de actualizaciones.
- Los eventos de rastreo se registran de forma incompleta.
- Las incidencias (daño, pérdida, rechazo) son difíciles de escalar y dar seguimiento.
- Las evidencias de entrega están dispersas y no siempre son consultables.

**Oportunidad:** un sistema que centralice el rastreo, formalice las reglas de excepción y dé visibilidad consistente a cada actor.

## 3. Stakeholders

| Rol | Interés / Participación |
|---|---|
| Remitente | Entrega el paquete, origina la guía y consulta el historial completo. |
| Empleado de sucursal | Recibe, pesa, mide y registra; corrige datos y autoriza cancelaciones tempranas. |
| Centro de distribución | Clasifica, transfiere y reporta eventos de rastreo (escaneos). |
| Repartidor | Hace el reparto final, captura evidencia e intentos fallidos. |
| Destinatario | Recibe el paquete; consulta estado y fecha estimada; reagenda o recoge. |
| Atención al Cliente | Resuelve incidencias y modifica la dirección durante el tránsito. |
| Supervisor de operaciones | Atiende alertas y escalamientos; declara pérdidas. |
| Supervisor de sucursal de origen | Decide reembolso o reposición por paquete dañado. |

## 4. Alcance

**Dentro del alcance**
- Registro de paquetes, cotización y generación de guía en sucursal.
- Seguimiento de estados con eventos de rastreo.
- Intentos de entrega, resguardo, reagendamiento y devolución.
- Evidencia de entrega (firma digital y foto), incluida la entrega a terceros.
- Incidencias: paquete dañado, rastreo sin actualización (alertas y escalamiento) y pérdida.
- Consulta de rastreo diferenciada para remitente y destinatario.

**Fuera del alcance:** envíos internacionales, facturación y cobranza detallada, integración con transportistas externos.

## 5. Necesidades del negocio (trazabilidad TR)

| ID | Necesidad |
|---|---|
| TR-01 | Reducir las llamadas a Atención al Cliente por falta de información de estatus. |
| TR-02 | Garantizar que cada cambio de estado genere un evento de rastreo visible. |
| TR-03 | Formalizar y agilizar el manejo de incidencias (daño, pérdida, ausencia). |
| TR-04 | Centralizar la evidencia de entrega para consulta rápida ante reclamos. |
| TR-05 | Detectar automáticamente envíos retrasados o sin actualización prolongada. |

## 6. Restricciones

- Peso máximo por paquete: **30 kg**; dimensiones máximas: **100 × 100 × 100 cm**.
- Máximo **2 intentos** de entrega.
- Resguardo máximo de **5 días hábiles** en el centro de distribución.
- Niveles de servicio: **Estándar** (3–5 días hábiles) y **Express** (24–48 h).
- Herramientas del curso: draw.io / Mermaid, GitHub, Python.

## 7. Supuestos

- El pago se realiza al generar la guía en sucursal (no se modela la cobranza).
- Los repartidores tienen dispositivo móvil para capturar firma y foto.
- Sucursales y centros reportan eventos en tiempo real.
- El destinatario puede ser distinto de quien recibe físicamente (tercero autorizado).

## 8. Decisiones del stakeholder (pendientes de la U2 resueltos)

| Pendiente U2 (§6.3) | Decisión v2.0 |
|---|---|
| ¿Quién paga el cambio de dirección en tránsito? | El **destinatario**, que es quien lo solicita: **$80 MXN** fijos. |
| ¿Porcentaje de reembolso si Express no cumple? | **50 %** del costo del envío. |
| ¿El destinatario puede consultar la evidencia? | **No** por ahora: solo Remitente y Atención al Cliente (se mantiene la respuesta P9). |
| Tope de compensación por pérdida | Valor declarado con **tope de $5,000 MXN**. |
| Fórmula de tarifa (BRD §1 no la definía) | Ver RN-03. |

## 9. Catálogo de reglas de negocio

Cada regla se identifica en las User Stories, el código (`src/domain`) y las pruebas (`tests/`).

| ID | Regla | Fuente | Historia |
|---|---|---|---|
| RN-01 | Peso ≤ 30 kg y cada dimensión ≤ 100 cm. Si se excede, no se genera guía estándar: **carga especial**. | BRD §6; P5 | US01 |
| RN-02 | Cada paquete recibe un **número de guía único** (formato `CBX-000000`). | BRD §1 | US01 |
| RN-03 | **Tarifa** = ($99 + $15 × kg cobrable) × factor de zona × factor de servicio. Kg cobrable = mayor entre peso real y peso volumétrico (L × A × H / 5000). Zona por código postal: mismos 2 primeros dígitos = local ×1.0; mismo primer dígito = regional ×1.3; otro = nacional ×1.6. Express ×1.8. | BRD §1; §8 | US01 |
| RN-04 | Los estados avanzan en orden: RECIBIDO → CLASIFICADO → EN_TRANSITO → CENTRO_DESTINO → EN_REPARTO → ENTREGADO. No se puede saltar ni retroceder (salvo las excepciones de RN-09, RN-13 y RN-18). | BRD §1 | US04 |
| RN-05 | **Todo cambio de estado genera un evento de rastreo** con estado, ubicación y fecha/hora. | BRD §1; TR-02 | US04 |
| RN-06 | Máximo **2 intentos** de entrega; al segundo fallido la guía pasa a **EN_RESGUARDO** y se notifica al destinatario. | BRD §6; P6 | US05 |
| RN-07 | La entrega solo se completa con **firma digital y foto**; solo existe un intento exitoso. | P9; TR-04 | US06 |
| RN-08 | El **remitente** ve la línea de tiempo completa del envío; solo el remitente de esa guía (se valida con su teléfono). | P12; U3 supuesto 4 | US09 |
| RN-09 | Solo se puede **cancelar** una guía en estado RECIBIDO; lo autoriza el empleado de sucursal. Después solo se permite redirección. | P2 | US02 |
| RN-10 | El empleado de sucursal puede **corregir origen/destino** solo antes de CLASIFICADO, sin generar nueva guía. | P3 | US03 |
| RN-11 | En **entrega a tercero** se registran nombre, firma y foto de quien recibe (vecino/portero). | P8 | US07 |
| RN-12 | El **destinatario** ve solo el estado actual y la fecha estimada, sin historial interno. | P12 | US08 |
| RN-13 | En resguardo el destinatario puede **reagendar una sola vez** (vuelve a EN_REPARTO; si esa visita también falla, regresa a EN_RESGUARDO) o **recoger** en el centro, dentro de **5 días hábiles**. Vencido el plazo, la guía pasa a **DEVUELTO** (devolución al remitente). | P7; BRD §6 | US10 |
| RN-14 | **Cambio de dirección** solo en EN_TRANSITO o CENTRO_DESTINO, con identidad validada; cobra $80 al destinatario y **anula la garantía** de tiempo de entrega. | P13; §8 | US11 |
| RN-15 | Una guía activa con **24 h sin cambio de estado** genera una **alerta por retraso**. | P4; P11 | US12 |
| RN-16 | Una alerta sin resolver por **48 h** se **escala** a un supervisor de operaciones. | P11 | US13 |
| RN-17 | Un **folio por paquete dañado** requiere evidencia fotográfica y se asigna al supervisor de la sucursal de origen, que decide **reembolso o reposición**. | P10 | US14 |
| RN-18 | Una guía con **más de 10 días naturales** sin actualización puede declararse **PERDIDO**; compensación = valor declarado con tope de **$5,000**; el caso se cierra. | P15; §8 | US15 |
| RN-19 | Si un envío **Express** se entrega después de 48 h (y conserva la garantía), aplica **reembolso del 50 %** del costo. | P14; §8 | US06 |
| RN-20 | **Fecha estimada**: Estándar = 5 días hábiles; Express = 2 días naturales (48 h) desde la generación de la guía. | P14 | US01, US08 |

### 9.1 Ciclo de vida de la guía (máquina de estados)

| Estado | Puede pasar a | Disparador |
|---|---|---|
| RECIBIDO | CLASIFICADO, CANCELADO | Escaneo de ingreso (US04) / cancelación (US02) |
| CLASIFICADO | EN_TRANSITO | Escaneo de salida (US04) |
| EN_TRANSITO | CENTRO_DESTINO, PERDIDO | Escaneo de ingreso en destino / declaración de pérdida |
| CENTRO_DESTINO | EN_REPARTO, PERDIDO | Salida a ruta |
| EN_REPARTO | ENTREGADO, EN_RESGUARDO, PERDIDO | Entrega (US06/US07) / 2º intento fallido o falla de la visita reagendada (US05, US10) |
| EN_RESGUARDO | EN_REPARTO, ENTREGADO, DEVUELTO | Reagendar / recoger en centro / vencen 5 días hábiles (US10) |
| ENTREGADO, CANCELADO, DEVUELTO, PERDIDO | — (finales) | — |

## 10. Criterios de éxito

- 100 % de los cambios de estado generan un evento de rastreo (RN-05).
- Reducción medible de llamadas por consultas de estatus (consultas US08/US09 disponibles 24/7).
- Tiempo de resolución de incidencias medible con folio (US14, US15).
- Cumplimiento del tiempo comprometido con compensación automática (RN-19).

## 11. Historial de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 03/09/2026 | BRD original con entrevista simulada (U2). |
| 1.1 | 16/10/2026 | U3: hallazgos H-01 (segundo intento en BPMN), H-02 (imagen de modelo de dominio de otro caso), H-03 (Value Objects). |
| 2.0 | 05/11/2026 | PIA: decisiones §8, catálogo RN-01…RN-20, máquina de estados completa (EN_RESGUARDO, DEVUELTO, CANCELADO, PERDIDO). |
