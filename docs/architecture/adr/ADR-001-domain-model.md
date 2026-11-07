# ADR-001: Domain Model para comandos y consultas directas para lectura

| Campo | Contenido |
|---|---|
| **Estado** | Aceptada (2026-10-12, U3) · Ratificada en el PIA (2026-11-05) |
| **Contexto** | US01, US04, US05 y US06 tienen reglas de límites, orden de estados, máximo de 2 intentos y evidencia obligatoria. El BRD reporta eventos de rastreo incompletos. En el PIA se suman US02, US03, US07, US10–US15, que también cambian el estado de la guía. US08 y US09 solo consultan. |
| **Alternativas** | Transaction Script (rápido, pero repite validaciones y puede olvidar el evento de rastreo); Table Module (acopla el dominio a las tablas). Calificación ponderada de la U3: Transaction Script 1.75, Table Module 2.55, **Domain Model 4.45**. |
| **Decisión** | Domain Model con los agregados `Guia` e `Incidencia` para todo lo que cambia estado; consultas directas a un modelo de lectura para US08 y US09. |
| **Consecuencias** | (+) Las 20 reglas viven en `src/domain` y se prueban sin base de datos. (−) Más clases y mapeo dominio ↔ ORM en los repositorios. |
| **Trazabilidad** | US01–US15; RN-01…RN-20; TR-02, TR-04 |
