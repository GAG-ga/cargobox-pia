# Glosario de dominio — CargoBox (lenguaje ubicuo)

El mismo término se usa en el negocio, en los documentos, en el código (`src/domain`) y en la API. Columna **En el código**: nombre de la clase, atributo o error.

## Conceptos del negocio

| Término | Definición | En el código |
|---|---|---|
| Guía | Envío de un paquete desde que se registra en sucursal hasta su cierre; es lo que el cliente rastrea. Raíz del agregado. | `Guia` |
| Número de guía | Código único impreso en la etiqueta (`CBX-000000`). | `NumeroGuia` |
| Remitente | Persona que entrega el paquete en sucursal y origina el envío. | `Guia.remitente: Persona` |
| Destinatario | Persona designada para recibir el paquete. | `Guia.destinatario: Persona` |
| Dirección | Domicilio de entrega; su código postal determina la zona tarifaria. | `Direccion` |
| Empleado de sucursal | Recibe, pesa, mide, registra, corrige y cancela guías tempranas. | actor de `registrar_guia`, `cancelar`, `corregir_destino` |
| Sucursal | Punto donde el remitente entrega el paquete y se genera la guía. | `Guia.sucursal_origen` |
| Centro de distribución | Instalación donde se clasifican y transfieren los paquetes. | `Ubicacion` de los escaneos |
| Repartidor | Encargado del reparto final y de capturar evidencia. | actor de `registrar_entrega`, `registrar_intento_fallido` |
| Atención al Cliente | Área que resuelve incidencias y cambia la dirección en tránsito. | actor de `cambiar_direccion`, `abrir_folio_dano` |
| Supervisor de operaciones | Atiende alertas y escalamientos y declara pérdidas. | `Alerta.asignada_a`, `declarar_perdida` |
| Supervisor de sucursal de origen | Decide reembolso o reposición por paquete dañado. | `Incidencia.asignada_a` |
| Peso / Dimensiones | Medidas tomadas en sucursal; límite 30 kg y 100 × 100 × 100 cm. | `Peso`, `Dimensiones` |
| Peso volumétrico | Largo × ancho × alto / 5000; se cobra el mayor entre real y volumétrico. | `Dimensiones.peso_volumetrico` |
| Carga especial | Paquete que excede peso o dimensiones máximas; no recibe guía estándar. | `CargaEspecialRequerida` |
| Nivel de servicio | Estándar (5 días hábiles) o Express (48 h). | `NivelServicio` |
| Zona | Local, regional o nacional según los códigos postales de origen y destino. | `Zona` |
| Tarifa | Precio del envío calculado por el cotizador. | `Cotizador`, `Dinero` |
| Valor declarado | Monto que el remitente asigna al contenido; base de la compensación. | `Guia.valor_declarado` |
| Fecha estimada | Fecha comprometida de entrega según el nivel de servicio. | `Guia.fecha_estimada` |
| Garantía de tiempo | Compromiso de entrega; se pierde al cambiar la dirección en tránsito. | `Guia.con_garantia` |
| Estado del paquete | Fase del ciclo de vida de la guía. | `EstadoGuia` |
| Evento de rastreo | Registro de cada cambio de estado con ubicación y fecha/hora. | `EventoRastreo` |
| Escaneo | Lectura de la guía al entrar o salir de un centro; cambia el estado. | `Guia.registrar_escaneo` |
| Intento de entrega | Cada visita del repartidor al domicilio (máximo 2). | `IntentoEntrega` |
| Evidencia de entrega | Firma digital, foto y nombre de quien recibe. | `EvidenciaEntrega` |
| Entrega a tercero | Recepción por una persona distinta al destinatario (vecino, portero). | `EvidenciaEntrega.es_tercero` |
| Resguardo | Retención en el centro tras 2 intentos fallidos; máximo 5 días hábiles. | `EstadoGuia.EN_RESGUARDO` |
| Reagendamiento | Nueva visita solicitada por el destinatario durante el resguardo (una sola vez). | `Guia.reagendar` |
| Devolución | Regreso del paquete al remitente al vencer el resguardo. | `EstadoGuia.DEVUELTO` |
| Cancelación | Anulación de una guía que sigue en RECIBIDO. | `EstadoGuia.CANCELADO` |
| Cargo adicional | Costo del cambio de dirección ($80) que paga el destinatario. | `Guia.cargos_adicionales` |
| Reembolso Express | 50 % del costo cuando un Express se entrega después de 48 h. | `Guia.reembolso` |
| Incidencia | Caso abierto por una excepción (daño, retraso, pérdida). | `Incidencia` |
| Folio de incidencia | Identificador para dar seguimiento a una incidencia. | `Incidencia.folio` |
| Alerta por retraso | Incidencia automática tras 24 h sin cambio de estado. | `TipoIncidencia.RETRASO` |
| Escalamiento | Reasignación a supervisor de una alerta con 48 h sin resolver. | `EstadoIncidencia.ESCALADA` |
| Pérdida | Declaración formal de una guía con más de 10 días naturales sin actualización. | `EstadoGuia.PERDIDO` |
| Compensación | Pago por pérdida: valor declarado con tope de $5,000. | `Guia.compensacion` |

## Errores de dominio (mensajes que ve el usuario)

| Error | Cuándo ocurre | Regla |
|---|---|---|
| `CargaEspecialRequerida` | El paquete excede 30 kg o 100 cm por lado. | RN-01 |
| `TransicionEstadoInvalida` | El cambio de estado no sigue el orden del recorrido. | RN-04 |
| `LimiteIntentosExcedido` | Se intenta un tercer intento de entrega. | RN-06 |
| `EvidenciaIncompleta` | Falta firma, foto o nombre de quien recibe. | RN-07, RN-11, RN-17 |
| `EntregaYaRegistrada` | La guía ya tiene un intento exitoso. | RN-07 |
| `CancelacionNoPermitida` | Se intenta cancelar una guía ya clasificada. | RN-09 |
| `CorreccionNoPermitida` | Se intenta corregir datos de una guía clasificada. | RN-10 |
| `ReagendamientoNoPermitido` | Se intenta reagendar fuera de resguardo o por segunda vez. | RN-13 |
| `CambioDireccionNoPermitido` | La guía no está en tránsito ni en centro destino. | RN-14 |
| `IdentidadNoValidada` | Se cambia la dirección sin validar identidad. | RN-14 |
| `PerdidaNoDeclarable` | La guía no supera 10 días sin actualización o ya está cerrada. | RN-18 |
| `GuiaNoEncontrada` | No existe una guía con el número consultado. | RN-02 |
| `AccesoDenegado` | Alguien que no es el remitente intenta ver el historial completo. | RN-08 |
