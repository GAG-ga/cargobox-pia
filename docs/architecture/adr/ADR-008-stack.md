# ADR-008: Python 3.12 + FastAPI + SQLAlchemy 2 + PostgreSQL

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-11-05, PIA) · **Reemplaza la elección de MySQL del ADR-003** |
| **Contexto** | El PIA exige API REST documentada con Swagger/OpenAPI activo en producción, persistencia, Docker Compose y despliegue en una plataforma gratuita. El equipo ya usa Python, pytest y SQLAlchemy en la Unidad 5. |
| **Alternativas** | Node.js + Express (Swagger manual); Java + Spring Boot (curva y tiempo de arranque mayores); MySQL (ADR-003 original) vs PostgreSQL. |
| **Decisión** | **FastAPI** (genera OpenAPI y Swagger UI automáticamente a partir de los esquemas Pydantic), **SQLAlchemy 2** como ORM (ya conocido de la U5), **PostgreSQL 16** como motor (Render ofrece PostgreSQL gestionado gratuito; MySQL no) y **pytest** para pruebas. En pruebas unitarias e integración rápida se usa SQLite en memoria; en Docker Compose y CI las pruebas de integración corren contra PostgreSQL. |
| **Consecuencias** | (+) Swagger sin trabajo extra; mismo lenguaje que la U5; despliegue gratuito. (−) Se cambia el motor del ADR-003: el código del dominio no se ve afectado porque depende de interfaces de repositorio (inversión de dependencias). |
| **Trazabilidad** | Requisitos PIA: API REST, OpenAPI, persistencia, despliegue |
