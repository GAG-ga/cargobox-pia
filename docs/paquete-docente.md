# Paquete de datos del docente — ejecución y diferencias con nuestro diseño

El curso entregó un paquete de pruebas para CargoBox (`datos/`): 40 actores, 20 servicios de catálogo,
60 operaciones con 117 líneas de detalle, **120 casos de reglas** y **20 pruebas de transición**.
Las instrucciones aclaran que es un *modelo de pruebas propuesto* y que, si difiere de nuestro BRD,
hay que **documentar las diferencias y adaptar fixtures y oráculos** sin reemplazar nuestros
requerimientos. Este documento hace eso.

## 1. Cómo se ejecuta

```bash
python scripts/ejecutar_paquete_docente.py     # llena resultado_alumno y guarda la evidencia
pytest tests/unit/test_paquete_docente.py -v    # pruebas automatizadas del paquete (corren en CI)
```

| Pieza | Capa | Archivo |
|---|---|---|
| `OperacionServicio`, `LineaOperacion`, `Remitente`, `ServicioCatalogo` | domain | `src/domain/operacion_servicio.py` |
| Specifications `PuedeProcesarse`, `BeneficioReferencia`, `ServiciosConCapacidad` (+ 6 simples) | domain | `src/domain/operacion_servicio.py` |
| Error `OperacionNoProcesable` | domain | `src/domain/errores.py` |
| Caso de uso: evaluar casos y ejecutar transiciones | application | `src/application/validacion_paquete.py` |
| Lector CSV UTF-8 con BOM y validación de claves foráneas | infrastructure | `src/infrastructure/datos_csv.py` |
| Resultados | docs | `docs/paquete-docente/casos_prueba_resultados.csv`, `transiciones_prueba_resultados.csv` |

Los cambios de estado usan **la misma `MaquinaEstadosGuia`** de la guía (ADR-007) y cada cambio publica
el evento de dominio `EstadoCambiado` (ADR-004). El total se calcula con `Decimal` mediante el
Value Object `Dinero`: `total = Σ precio_mxn × cantidad`.

## 2. Reglas del paquete como Specifications (AND / OR / NOT)

```python
class PuedeProcesarse(Specification):        # activo AND con líneas AND autorizada
    def __init__(self):
        self._spec = RemitenteActivo() & TieneServicios() & Autorizada()

class BeneficioReferencia(Specification):     # preferente AND total ≥ 1500 AND NOT promoción
    def __init__(self, umbral=Dinero(Decimal("1500"))):
        self._spec = RemitentePreferente() & TotalAlMenos(umbral) & ~PromocionActiva()
```

El OR se demuestra en `test_combinacion_or_de_specifications`. Antes de aprobar o completar, la
operación exige `PuedeProcesarse() & ServiciosConCapacidad()` (servicio habilitado y cantidad ≤ capacidad).

## 3. Resultados

### 120 casos de reglas (`casos_prueba.csv`)

| Tipo de prueba | CUMPLE | NO_CUMPLE | Motivos de NO_CUMPLE |
|---|---|---|---|
| `validar_operacion` (puede_procesarse) | 43 | 17 | 10 operaciones de remitentes inactivos (5 actores), 7 sin autorización y 2 sin líneas (CAR-O013, CAR-O039); 2 operaciones fallan por dos motivos |
| `evaluar_beneficio` (beneficio_referencia) | 10 | 50 | 48 remitentes no preferentes, 1 con promoción activa y 1 con total < $1,500 |

Cada fila conserva su evidencia, por ejemplo `CAR-T013 → NO_CUMPLE · activo=1; lineas=0; autorizado=1`.

### 20 transiciones (`transiciones_prueba.csv`)

| Acción | Interpretación en nuestro dominio | Resultado |
|---|---|---|
| `aprobar` | Escaneo de ingreso: RECIBIDO → CLASIFICADO (requiere precondiciones) | 1 OK; 3 `OperacionNoProcesable` (servicio CAR-P011 deshabilitado o remitente inactivo) |
| `cancelar` | RECIBIDO → CANCELADO (RN-09) | 4 OK |
| `completar` | Recorrido completo CLASIFICADO → EN_TRANSITO → CENTRO_DESTINO → EN_REPARTO → ENTREGADO | 3 OK (5 `EstadoCambiado` + `EntregaCompletada`); 1 `OperacionNoProcesable` |
| `repetir_aprobacion` | Aprobar dos veces: la segunda es CLASIFICADO → CLASIFICADO | 1 `TransicionEstadoInvalida` (queda en CLASIFICADO); 3 `OperacionNoProcesable` |
| `saltar_estado` | RECIBIDO → EN_TRANSITO sin clasificar (RN-04) | 4 `TransicionEstadoInvalida` (queda en RECIBIDO) |

## 4. Diferencias entre el modelo propuesto y nuestro BRD

| Aspecto | Paquete del docente | Nuestro BRD / diseño (U2–U3) | Decisión |
|---|---|---|---|
| Entidad principal | "Operación" de un remitente con líneas del catálogo | **Guía** (agregado) de un paquete con peso, dimensiones, zona y nivel de servicio | La operación se modela aparte (`OperacionServicio`) y reutiliza nuestra máquina de estados, Specifications y eventos. |
| Estados | 5: RECIBIDO, CLASIFICADO, EN_TRANSITO, ENTREGADO, CANCELADO | 10 (BRD §9.1): se agregan CENTRO_DESTINO, EN_REPARTO, EN_RESGUARDO, DEVUELTO y PERDIDO | Se conserva la tabla de 10 estados. Los 5 del paquete existen en ella. |
| Flujo feliz | RECIBIDO → CLASIFICADO → EN_TRANSITO → ENTREGADO | ... → EN_TRANSITO → CENTRO_DESTINO → EN_REPARTO → ENTREGADO | `completar` recorre nuestro flujo completo. Un salto EN_TRANSITO → ENTREGADO sería inválido para nosotros. |
| Precio | `precio_mxn × cantidad` de un catálogo fijo | Tarifa RN-03 = ($99 + $15 × kg cobrable) × zona × servicio | El total del paquete se calcula como indica el docente. La guía sigue cotizando con RN-03. |
| `puede_procesarse` | activo AND línea AND autorización | Nuestras precondiciones son RN-01 (límites del paquete) y los datos completos de la guía | Se implementa como Specification adicional sin modificar RN-01. |
| `beneficio_referencia` | preferente AND total ≥ 1500 AND NOT promoción | No existe en nuestro BRD (no hay clientes preferentes ni promociones) | Se implementa solo para el paquete. **No** afecta la tarifa de la guía. |
| Capacidad / stock | `capacidad_o_stock` y `habilitado` por servicio | Nuestro BRD no maneja inventario de servicios | `ServiciosConCapacidad` valida habilitado y cantidad ≤ capacidad por línea. |
| Autorización | Bandera `autorizado` por operación | La guía no requiere autorización: la registra el empleado de sucursal | Precondición solo del modelo del paquete. |
| Entrega | `completar` sin evidencia | RN-07: firma digital + foto obligatorias | En la guía real la entrega exige evidencia (`POST /guias/{n}/entrega`). En el paquete se simula el cierre. |
| Códigos HTTP | 200/201, 400/409/422 y 404 | 201 al crear, 404 si no existe, 409 por transición/estado, 422 por datos o reglas, 403 por acceso | Coincide con el contrato del paquete; agregamos 403 (RN-08). |

> Los resultados esperados del docente no están en el paquete del alumno. Si el oráculo del docente
> interpreta `completar` o `repetir_aprobacion` de otra forma, solo hay que cambiar el diccionario
> `ACCIONES` de `validacion_paquete.py`.
