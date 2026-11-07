# Documento de decisiones técnicas — CargoBox

Resume **qué** se construye, **con qué** y **por qué**. Cada decisión importante tiene su ADR en [`adr/`](adr/README.md).

## 1. Vista general

CargoBox es una API REST que implementa el proceso de envíos del BRD: registro y cotización de guías, rastreo por escaneos, entregas con evidencia, resguardo y devolución, incidencias y consultas para remitente y destinatario.

```
Cliente (Swagger UI / app de sucursal / web de rastreo)
        │ HTTP/JSON
        ▼
   api/          FastAPI: routers, esquemas Pydantic, errores → mensajes
        │
        ▼
   application/  Application Services (1 método = 1 caso de uso), comandos, DTOs, puertos
        │
        ▼
   domain/       Guia, Incidencia, Value Objects, MaquinaEstadosGuia, Specifications,
                 Cotizador, eventos y errores de dominio, interfaces de repositorio
        ▲
        │ implementa
   infrastructure/ SQLAlchemy + PostgreSQL, Unit of Work, almacén de evidencias, publicador
```

Diagramas: [`diagramas/`](diagramas/) (capas, clases, secuencias y despliegue).

## 2. Stack tecnológico

| Necesidad | Tecnología | Por qué (ADR) |
|---|---|---|
| Lenguaje | Python 3.12 | Mismo lenguaje que la Unidad 5 (ADR-008) |
| API REST + OpenAPI | FastAPI + Pydantic | Swagger UI automático en `/docs` (ADR-008) |
| Persistencia | SQLAlchemy 2 + PostgreSQL 16 | ORM conocido; PostgreSQL gratuito en Render (ADR-008) |
| Pruebas | pytest, pytest-cov | Cobertura ≥ 80 % (U5) |
| Calidad | Ruff | Lint en CI (U5) |
| Contenedores | Docker + Docker Compose | DB + App + Tests reproducibles (ADR-010) |
| CI/CD | GitHub Actions | Lint → pruebas → cobertura → build de imagen (U5) |
| Despliegue | Render (Web Service + PostgreSQL) | Gratuito, conectado a GitHub (ADR-010) |

## 3. Patrones de diseño y su justificación

| Patrón | Problema de CargoBox que resuelve | Dónde está | ADR |
|---|---|---|---|
| **Domain Model** | 20 reglas con estados e invariantes; con scripts sueltos se repetiría el problema de eventos incompletos del BRD. | `src/domain/` | 001 |
| **Aggregate** | La guía, sus eventos, intentos y evidencia deben cambiar juntos y de forma consistente. | `Guia`, `Incidencia` | 002 |
| **Value Object** | Peso, dimensiones, dinero o número de guía inválidos no deben poder existir (RN-01, RN-02). | `value_objects.py` | 002 |
| **State Machine** | 10 estados con transiciones permitidas, finales y excepciones (RN-04). | `estados.py` → `MaquinaEstadosGuia` | 007 |
| **Specification** | Las mismas condiciones (¿cancelable?, ¿requiere alerta?, ¿perdida?) se usan en el dominio y en el monitoreo. | `especificaciones.py` | 006 |
| **Strategy** | La tarifa cambia por nivel de servicio; agregar un nivel no debe modificar el cotizador (RN-03). | `PoliticaTarifa`: `TarifaEstandar`, `TarifaExpress` | 006/U3 |
| **Domain Service** | La tarifa usa peso, dimensiones, zona y nivel: no pertenece a una sola entidad. | `Cotizador` | U3 |
| **Repository** | El dominio no debe conocer SQL ni el ORM. | Interfaces en `domain/repositorios.py`; implementación en `infrastructure/` | 009 |
| **Unit of Work** | Un caso de uso = una transacción; ante un error de dominio no se guarda nada. | `application/puertos.py` + `infrastructure/unit_of_work.py` | 005 |
| **Service Layer** | Los casos de uso coordinan sin contener reglas. | `application/servicios.py` | 005 |
| **Domain Events (Observer)** | Notificar al destinatario/remitente sin acoplar el dominio a correos. | `domain/eventos.py`, `PublicadorEventos` | 004 |
| **CQRS básico** | Remitente y destinatario ven información distinta y solo leen. | `ConsultaRastreoQueryService` | 003 |
| **DTO** | La API nunca expone el agregado ni el modelo ORM. | `application/dtos.py`, `api/esquemas.py` | 009 |
| **Ports & Adapters / Inyección de dependencias** | Cambiar PostgreSQL, el almacén de fotos o el reloj sin tocar el dominio; probar con dobles. | `application/puertos.py`, `api/dependencias.py` | 009 |

## 4. Principios SOLID aplicados

| Principio | Cómo se cumple en CargoBox | Evidencia en el código |
|---|---|---|
| **S** — Responsabilidad única | Cada clase tiene una razón para cambiar: `Guia` protege reglas, `MaquinaEstadosGuia` solo sabe qué transiciones existen, cada `Specification` evalúa una condición, los servicios solo coordinan, los routers solo traducen HTTP. | `estados.py`, `especificaciones.py`, `servicios.py`, `api/rutas/` |
| **O** — Abierto/cerrado | Nuevo nivel de servicio = nueva `PoliticaTarifa`; nueva condición = nueva `Specification`; nueva reacción a un evento = nuevo suscriptor. Nada existente se modifica. | `cotizador.py`, `especificaciones.py`, `eventos.py` |
| **L** — Sustitución de Liskov | Cualquier `GuiaRepository` (SQL o en memoria) o `AlmacenEvidencias` (disco o Mock) cumple el mismo contrato; las pruebas usan sustitutos sin cambiar los servicios. | `repositorios.py`, `tests/` |
| **I** — Segregación de interfaces | La consulta depende solo de `HistorialRastreoReader` (lectura); los comandos dependen de `GuiaRepository`. El servicio de entrega es el único que conoce `AlmacenEvidencias`. | `puertos.py` |
| **D** — Inversión de dependencias | Dominio y aplicación dependen de interfaces; FastAPI, SQLAlchemy y el sistema de archivos se conectan desde afuera en `api/dependencias.py`. | `dependencias.py` |

## 5. Configuración (12-Factor)

| Variable | Uso | Ejemplo (`.env.example`) |
|---|---|---|
| `DATABASE_URL` | Conexión a la base | `postgresql+psycopg://cargobox:cargobox@db:5432/cargobox` |
| `APP_ENV` | `local`, `test` o `production` | `local` |
| `EVIDENCIAS_DIR` | Carpeta del almacén de firmas y fotos | `/data/evidencias` |

Ningún secreto está en el código ni en el repositorio.

## 6. Riesgos y decisiones pendientes

| Riesgo | Mitigación |
|---|---|
| Publicar eventos después del commit puede perder notificaciones si el proceso cae. | Documentado como evolución con patrón Outbox (ADR-004). |
| El plan gratuito de Render duerme el servicio. | Abrir `/docs` unos minutos antes de la demo. |
| Las reglas de tiempo necesitan un disparador. | `POST /monitoreo/ejecutar` con fecha simulada para la demo (ADR-011). |
| Días festivos no considerados en "días hábiles". | Se cuentan lunes a viernes; los festivos quedan como mejora. |
