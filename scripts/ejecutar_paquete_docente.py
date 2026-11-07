"""Ejecuta los 120 casos y las 20 transiciones del paquete del docente y guarda los resultados.

    python scripts/ejecutar_paquete_docente.py
        → docs/paquete-docente/casos_prueba_resultados.csv
        → docs/paquete-docente/transiciones_prueba_resultados.csv
"""
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.application.validacion_paquete import ejecutar_paquete  # noqa: E402
from src.infrastructure.datos_csv import cargar_operaciones, escribir_csv, leer_csv  # noqa: E402

DATOS = RAIZ / "datos"
SALIDA = RAIZ / "docs" / "paquete-docente"


def main() -> None:
    casos, trans = ejecutar_paquete(
        leer_csv(DATOS / "casos_prueba.csv"),
        leer_csv(DATOS / "transiciones_prueba.csv"),
        lambda: cargar_operaciones(DATOS),
    )
    escribir_csv(SALIDA / "casos_prueba_resultados.csv", casos)
    escribir_csv(SALIDA / "transiciones_prueba_resultados.csv", trans)

    print(f"Casos de reglas: {len(casos)}")
    for (tipo, res), n in sorted(Counter((c["tipo_prueba"], c["resultado_alumno"]) for c in casos).items()):
        print(f"  {tipo:<18} {res:<10} {n}")
    print(f"Transiciones: {len(trans)}")
    for (acc, res, exc), n in sorted(
            Counter((t["accion_sugerida"], t["estado_final"], t["excepcion"]) for t in trans).items()):
        print(f"  {acc:<19} → {res:<12} {exc:<26} {n}")
    print(f"Resultados en {SALIDA.relative_to(RAIZ)}/")


if __name__ == "__main__":
    main()
