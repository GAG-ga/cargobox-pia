# ADR-009: Arquitectura por capas con puertos y adaptadores

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-11-05, PIA) |
| **Contexto** | El PIA exige `src/` separado en `domain`, `application`, `infrastructure` y `api`, y que el dominio no dependa de detalles técnicos. |
| **Alternativas** | Estructura por tipo de archivo (models/, routes/); estructura por historia de usuario. |
| **Decisión** | Cuatro capas con dependencias **solo hacia adentro**: `api → application → domain` y `infrastructure → application/domain`.<br>• `domain`: agregados, Value Objects, máquina de estados, especificaciones, cotizador, eventos, errores e **interfaces** de repositorio. No importa FastAPI ni SQLAlchemy.<br>• `application`: comandos, servicios, DTOs y puertos (`UnitOfWork`, `PublicadorEventos`, `AlmacenEvidencias`, `Reloj`).<br>• `infrastructure`: SQLAlchemy (modelos, repositorios, Unit of Work), almacén de evidencias, publicador, configuración por variables de entorno.<br>• `api`: routers FastAPI, esquemas Pydantic y traducción de errores de dominio a mensajes para el cliente.<br>El ensamblado (inyección de dependencias) se hace en `api/dependencias.py`. |
| **Consecuencias** | (+) El dominio se prueba sin base de datos ni HTTP; cambiar de PostgreSQL a otro motor solo toca `infrastructure`. (−) Mapeo explícito dominio ↔ ORM ↔ esquemas. |
| **Trazabilidad** | Estructura mínima del PIA; SOLID-D |
