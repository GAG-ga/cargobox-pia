# ADR-010: Docker Compose, configuración 12-Factor y despliegue en Render

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-11-05, PIA) |
| **Contexto** | El PIA exige un entorno reproducible con DB + App + Tests, configuración separada del código y un despliegue funcional con Swagger activo. |
| **Alternativas** | Instalación manual; Railway; Fly.io. |
| **Decisión** | • `Dockerfile` de la aplicación (uvicorn).<br>• `docker-compose.yml` con tres servicios: `db` (postgres:16), `app` (API en el puerto 8000) y `tests` (pytest con cobertura contra la misma base).<br>• Configuración **solo por variables de entorno** (`DATABASE_URL`, `APP_ENV`, `EVIDENCIAS_DIR`); `.env.example` sin secretos.<br>• **Render**: Web Service desde el repositorio de GitHub + PostgreSQL gestionado; `DATABASE_URL` se inyecta como variable de entorno. Swagger queda en `/docs`. |
| **Consecuencias** | (+) Cualquier integrante levanta todo con `docker compose up`; el mismo código corre en local, CI y producción. (−) El plan gratuito de Render "duerme" el servicio sin tráfico (primer request lento en la demo). |
| **Trazabilidad** | Requisitos PIA: Docker Compose, 12-Factor, despliegue, Swagger |
