"""Genera docs/api/openapi.json a partir del código (o verifica que esté actualizado).

    python scripts/exportar_openapi.py              → escribe el archivo
    python scripts/exportar_openapi.py --verificar  → falla si el archivo no coincide (CI)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.api.main import crear_app  # noqa: E402
from src.infrastructure.config import Configuracion  # noqa: E402

DESTINO = Path(__file__).resolve().parents[1] / "docs" / "api" / "openapi.json"


def generar() -> str:
    app = crear_app(Configuracion("sqlite:///:memory:", "docs", "/tmp/evidencias"))
    return json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    contenido = generar()
    if "--verificar" in sys.argv:
        actual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if actual != contenido:
            sys.exit("docs/api/openapi.json está desactualizado: ejecuta scripts/exportar_openapi.py")
        print("OpenAPI actualizado")
    else:
        DESTINO.parent.mkdir(parents=True, exist_ok=True)
        DESTINO.write_text(contenido, encoding="utf-8")
        print(f"Escrito {DESTINO}")
