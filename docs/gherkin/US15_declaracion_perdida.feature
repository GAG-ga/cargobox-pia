# language: es
@US15 @RN-18
Característica: Declaración de pérdida e indemnización
  Como supervisor de operaciones
  Quiero declarar como perdido un paquete con más de 10 días naturales sin actualización
  Para emitir la compensación y cerrar el caso

  Escenario: Pérdida con compensación igual al valor declarado
    Dado una guía en "EN_TRANSITO" con valor declarado de $1,200.00 y 11 días sin actualización
    Cuando el supervisor la declara perdida
    Entonces la guía queda en estado "PERDIDO"
    Y la compensación es de $1,200.00

  Escenario: La compensación respeta el tope de $5,000
    Dado una guía con valor declarado de $8,000.00 y 11 días sin actualización
    Cuando el supervisor la declara perdida
    Entonces la compensación es de $5,000.00

  Escenario: Con 10 días exactos todavía no se puede declarar pérdida
    Dado una guía con exactamente 10 días sin actualización
    Cuando el supervisor intenta declararla perdida
    Entonces el sistema responde "PerdidaNoDeclarable"
