# CargoBox — Plataforma de Envíos Nacionales

**Producto Integrador de Aprendizaje · Componentes de Lógica de Negocios · FIME UANL**
Caso 14 · Prof. Miguel Ángel Gómez Marroquín

| Integrante | Matrícula |
|---|---|
| Steven Roel Mejia Contreras | 2226582 |
| Juan José Montoya Zapata | 2226584 |
| Ivonne Niño Pérez | 2222984 |

API REST que implementa el proceso de envíos de CargoBox: registro y cotización de guías, rastreo por escaneos, entregas con evidencia, resguardo y devolución, incidencias (alertas, escalamiento, daño y pérdida) y consultas para remitente y destinatario. Construida con **DDD**, **Specification**, **State Machine** y arquitectura por capas.

- **Repositorio:** `https://github.com/GAG-ga/cargobox-pia`

- **Sistema desplegado (Swagger):** `https://cargobox-api.onrender.com/docs`

---

## 1. Ejecución rápida en Windows (sin Docker)

| Archivo | Qué hace |
|---|---|
| `INICIAR.bat` | Crea el entorno, instala dependencias, carga datos de demo en `cargobox_demo.db` (SQLite) y abre **Swagger** en `http://localhost:8000/docs`. Para reiniciar la demo, borrar `cargobox_demo.db`. |
| `PROBAR.bat` | Ruff + todas las pruebas con cobertura + abre el reporte HTML |

Requisito: Python 3.11 o superior.

## 2. Ejecución manual

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1      Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python scripts/cargar_demo.py              # opcional: guías de ejemplo
uvicorn src.api.main:app --reload          # http://localhost:8000/docs
```

Sin `DATABASE_URL` se usa SQLite (`cargobox.db`). Para PostgreSQL, definir la variable (ver `.env.example`).

## 3. Docker Compose (DB + App + Tests)

```bash
cp .env.example .env                       # ajustar la contraseña
docker compose up --build                  # PostgreSQL 16 + API → http://localhost:8000/docs
docker compose run --rm tests              # Ruff + pytest con cobertura contra PostgreSQL
docker compose exec app python scripts/cargar_demo.py   # datos de demo
docker compose down -v                     # apagar y borrar datos
```

## 4. Pruebas y calidad

```bash
ruff check src tests
pytest -v --cov=src --cov-report=term-missing --cov-fail-under=80
# contra PostgreSQL:
TEST_DATABASE_URL=postgresql+psycopg://usuario:clave@localhost:5432/cargobox_test pytest tests/api
```

| Tipo | Carpeta | Qué prueba |
|---|---|---|
| Unitarias | `tests/unit/` | Value Objects, **máquina de estados (los 100 pares de estados)**, Specifications, cotizador, calendario, incidencias |
| Aceptación | `tests/aceptacion/test_usXX_*.py` | **Un archivo por historia y una prueba por cada escenario Gherkin** (servicios con repositorios en memoria) |
| Integración | `tests/api/` | HTTP → servicios → SQLAlchemy → SQLite/PostgreSQL; errores con mensaje para el cliente |
| Trazabilidad | `tests/aceptacion/test_trazabilidad.py` | Cada `.feature` tiene su módulo de pruebas con al menos tantas pruebas como escenarios |

Resultado actual: **227 pruebas, cobertura 99.6 %** (mínimo exigido 80 %).

**CI/CD** (`.github/workflows/ci.yml`): en cada push → Ruff → pruebas con SQLite → pruebas de integración contra **PostgreSQL** con cobertura ≥ 80 % → verificación de OpenAPI → `docker build` y arranque de la imagen.

## 5. Arquitectura

```
src/
├── domain/          Reglas de negocio puras (sin FastAPI ni SQLAlchemy)
│   ├── guia.py              Aggregate Root Guía (10 operaciones de negocio)
│   ├── incidencia.py        Aggregate Root Incidencia (alertas y daños)
│   ├── estados.py           State Machine: tabla de transiciones (ADR-007)
│   ├── especificaciones.py  Specification: 9 reglas combinables (ADR-006)
│   ├── value_objects.py     NumeroGuia, Peso, Dimensiones, Dinero, Persona, Direccion…
│   ├── cotizador.py         Domain Service + Strategy de tarifas (RN-03)
│   ├── eventos.py, errores.py, calendario.py, repositorios.py (interfaces)
├── application/     Casos de uso: 5 Application Services, comandos, DTOs, puertos
├── infrastructure/  SQLAlchemy (modelos, repositorios, Unit of Work), almacén, publicador, config
└── api/             FastAPI: rutas, esquemas Pydantic, errores → mensajes, inyección de dependencias
```

Dependencias solo hacia adentro: `api → application → domain ← infrastructure`.
Documentación: [`docs/`](docs/README.md) — BRD, Gherkin, glosario, BPMN, **ADR-001…011**, patrones y SOLID, diagramas, trazabilidad y [OpenAPI](docs/api/openapi.json).

## 6. Endpoints

| Método | Ruta | Historia |
|---|---|---|
| POST | `/guias` | US01 Registrar guía y cotizar |
| POST | `/guias/{numero}/cancelacion` | US02 Cancelación temprana |
| PATCH | `/guias/{numero}/datos` | US03 Corrección de datos |
| POST | `/guias/{numero}/escaneos` | US04 Escaneo en centro |
| POST | `/guias/{numero}/intentos-fallidos` | US05 Intento fallido |
| POST | `/guias/{numero}/entrega` | US06 / US07 / US10 Entrega con evidencia (tercero o en centro) |
| POST | `/guias/{numero}/reagendamiento` | US10 Reagendar |
| PATCH | `/guias/{numero}/direccion` | US11 Cambio de dirección |
| POST | `/guias/{numero}/perdida` | US15 Declarar pérdida |
| GET | `/rastreo/{numero}` | US08 Consulta del destinatario |
| GET | `/rastreo/{numero}/historial?telefono=` | US09 Historial del remitente |
| GET | `/incidencias` | US12 / US13 Alertas e incidencias pendientes |
| POST | `/incidencias/danos` | US14 Folio por daño |
| POST | `/incidencias/{folio}/resolucion` | US14 Resolución |
| POST | `/monitoreo/ejecutar?ahora=` | US10 / US12 / US13 Reglas de tiempo (fecha simulada para la demo) |

Los errores de negocio responden con `{"error": "...", "mensaje": "..."}` en lenguaje del cliente, por ejemplo:

```json
{"error": "CargaEspecialRequerida",
 "mensaje": "El paquete excede 30 kg o 100 cm por lado: debe enviarse como carga especial y no puede recibir una guía estándar."}
```

## 7. Guion de demostración (Swagger)

Con los datos de `scripts/cargar_demo.py` (guías CBX-000001 a CBX-000005):

1. **US01 · RN-01/RN-03** — `POST /guias` con 10 kg → tarifa $249.00; repetir con 31 kg → error *carga especial*.
2. **US04 · State Machine** — `POST /guias/{n}/escaneos` con `EN_TRANSITO` sobre una guía nueva → *TransicionEstadoInvalida* (no se puede saltar CLASIFICADO).
3. **US08 vs US09 · CQRS** — `GET /rastreo/CBX-000001` (solo estado y mensaje) contra `GET /rastreo/CBX-000001/historial?telefono=8112345678` (línea de tiempo completa); con otro teléfono → *AccesoDenegado*.
4. **US05/US10 · RN-06** — la guía CBX-000003 está en resguardo tras 2 intentos; un tercer intento → *LimiteIntentosExcedido*; `POST /guias/CBX-000003/reagendamiento` → vuelve a reparto.
5. **US06 · RN-07** — `POST /guias/CBX-000005/entrega` sin foto → *EvidenciaIncompleta*; con foto → ENTREGADO.
6. **US12/US13 · Specification + reloj simulado** — `POST /monitoreo/ejecutar?ahora=<dentro de 2 días>` → alertas; `GET /incidencias`; repetir con +4 días → escaladas.
7. **US02** — `POST /guias/CBX-000002/cancelacion` → *CancelacionNoPermitida* (ya está en tránsito).

## 8. Despliegue en Render

1. Subir el repositorio a GitHub.
2. En [render.com](https://render.com): **New → Blueprint** → seleccionar el repositorio. Render lee `render.yaml` y crea el **Web Service (Docker)** y la base **PostgreSQL**; `DATABASE_URL` se conecta automáticamente.
3. Abrir `https://<servicio>.onrender.com/docs`.
4. (Opcional) Datos de demo: en la pestaña *Shell* del servicio, `python scripts/cargar_demo.py`.

> El plan gratuito "duerme" el servicio sin tráfico: abrir `/docs` unos minutos antes de la presentación.

## 9. Configuración (12-Factor)

| Variable | Descripción | Por defecto |
|---|---|---|
| `DATABASE_URL` | Conexión a la base (acepta `postgres://` de Render) | `sqlite:///./cargobox.db` |
| `APP_ENV` | `local`, `test`, `production` | `local` |
| `EVIDENCIAS_DIR` | Carpeta de firmas y fotos | `./evidencias` |
| `TEST_DATABASE_URL` | Base para pruebas de integración (opcional) | SQLite en memoria |
