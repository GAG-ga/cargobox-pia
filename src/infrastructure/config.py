"""Configuración 12-Factor: todo sale de variables de entorno (ADR-010)."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuracion:
    database_url: str
    app_env: str
    evidencias_dir: str

    @classmethod
    def desde_entorno(cls) -> "Configuracion":
        url = os.getenv("DATABASE_URL", "sqlite:///./cargobox.db")
        if url.startswith("postgres://"):  # formato que entrega Render
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return cls(database_url=url, app_env=os.getenv("APP_ENV", "local"),
                   evidencias_dir=os.getenv("EVIDENCIAS_DIR", "./evidencias"))
