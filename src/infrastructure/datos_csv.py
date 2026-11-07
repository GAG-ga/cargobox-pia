"""Lector del paquete de datos del docente (CSV UTF-8 con BOM) → objetos de dominio."""
import csv
from decimal import Decimal
from pathlib import Path

from src.domain.errores import DatoInvalido
from src.domain.operacion_servicio import (
    LineaOperacion,
    OperacionServicio,
    Remitente,
    ServicioCatalogo,
)
from src.domain.value_objects import Dinero


def leer_csv(ruta: Path) -> list[dict[str, str]]:
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def escribir_csv(ruta: Path, filas: list[dict[str, str]]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def cargar_operaciones(carpeta: Path) -> dict[str, OperacionServicio]:
    """Importa actores, catálogo, operaciones y detalle validando las claves foráneas."""
    remitentes = {
        f["actor_id"]: Remitente(f["actor_id"], f["activo"] == "1", f["es_preferente"] == "1")
        for f in leer_csv(carpeta / "actores.csv")
    }
    catalogo = {
        f["recurso_id"]: ServicioCatalogo(
            f["recurso_id"], f["descripcion"], Dinero(Decimal(f["precio_mxn"])),
            int(f["capacidad_o_stock"]), f["habilitado"] == "1",
        )
        for f in leer_csv(carpeta / "catalogo.csv")
    }
    lineas: dict[str, list[LineaOperacion]] = {}
    for f in leer_csv(carpeta / "detalle_operaciones.csv"):
        if f["recurso_id"] not in catalogo:
            raise DatoInvalido(f"Recurso inexistente en el detalle: {f['recurso_id']}")
        lineas.setdefault(f["operacion_id"], []).append(
            LineaOperacion(catalogo[f["recurso_id"]], int(f["cantidad"])))

    operaciones: dict[str, OperacionServicio] = {}
    for f in leer_csv(carpeta / "operaciones.csv"):
        if f["actor_id"] not in remitentes:
            raise DatoInvalido(f"Actor inexistente en la operación {f['operacion_id']}")
        operaciones[f["operacion_id"]] = OperacionServicio(
            operacion_id=f["operacion_id"],
            remitente=remitentes[f["actor_id"]],
            lineas=lineas.pop(f["operacion_id"], []),
            promocion_activa=f["promocion_activa"] == "1",
            autorizada=f["autorizado"] == "1",
        )
    if lineas:
        raise DatoInvalido(f"Detalle de operaciones inexistentes: {sorted(lineas)}")
    return operaciones
