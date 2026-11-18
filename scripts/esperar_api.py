"""Espera a que la API responda en /salud. Lo usa ABRIR_PANEL.bat.

    python scripts/esperar_api.py               → espera hasta 60 s; código 0 si respondió, 1 si no
    python scripts/esperar_api.py --segundos 1  → solo revisa si ya está corriendo
"""
import sys
import time
import urllib.request

URL = "http://localhost:8000/salud"


def responde() -> bool:
    try:
        with urllib.request.urlopen(URL, timeout=1) as respuesta:
            return respuesta.status == 200
    except OSError:
        return False


def esperar(segundos: int) -> bool:
    limite = time.monotonic() + segundos
    while True:
        if responde():
            return True
        if time.monotonic() >= limite:
            return False
        time.sleep(0.5)


if __name__ == "__main__":
    segundos = int(sys.argv[sys.argv.index("--segundos") + 1]) if "--segundos" in sys.argv else 60
    sys.exit(0 if esperar(segundos) else 1)
