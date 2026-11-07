"""Adaptador de AlmacenEvidencias: guarda firma y foto como archivos (ADR-009)."""
from pathlib import Path


class AlmacenEvidenciasDisco:
    def __init__(self, carpeta: str):
        self.carpeta = Path(carpeta)

    def guardar(self, numero_guia: str, firma: str, foto: str) -> str:
        destino = self.carpeta / numero_guia
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "firma.txt").write_text(firma, encoding="utf-8")
        (destino / "foto.txt").write_text(foto, encoding="utf-8")
        return str(destino)
