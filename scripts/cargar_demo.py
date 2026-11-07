"""Carga guías de ejemplo en distintos estados para la demostración en vivo.

    python scripts/cargar_demo.py        (usa DATABASE_URL o SQLite local)

Crea: una guía entregada, una en tránsito, una en resguardo, una cancelada y una Express
en reparto. Imprime los números para usarlos en Swagger.
"""
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.api.dependencias import Contenedor  # noqa: E402
from src.application.comandos import (  # noqa: E402
    CapturarEvidenciaCommand,
    RegistrarEscaneoCommand,
    RegistrarGuiaCommand,
)
from src.infrastructure.config import Configuracion  # noqa: E402

RUTA = [("CLASIFICADO", "CEDIS Monterrey"), ("EN_TRANSITO", "Ruta MTY-CDMX"),
        ("CENTRO_DESTINO", "CEDIS CDMX"), ("EN_REPARTO", "Unidad 12 CDMX")]


def guia(c, destinatario, cp, nivel="ESTANDAR", peso="10"):
    return c.envios().registrar_guia(RegistrarGuiaCommand(
        "Carlos Ruiz", "8112345678", destinatario, "8187654321", "Av. Universidad 100", "66450",
        "Calle Roble 10", cp, Decimal(peso), Decimal("40"), Decimal("30"), Decimal("20"), nivel,
        Decimal("1500"), "Sucursal San Nicolás")).numero


def avanzar(c, numero, hasta):
    for estado, lugar in RUTA:
        c.rastreo().registrar_escaneo(RegistrarEscaneoCommand(numero, estado, lugar))
        if estado == hasta:
            return


def main():
    c = Contenedor(Configuracion.desde_entorno())
    entregada = guia(c, "Ana López", "01000")
    avanzar(c, entregada, "EN_REPARTO")
    c.entregas().capturar_evidencia_entrega(CapturarEvidenciaCommand(
        entregada, "firma-ana.png", "foto-paquete.jpg", "Ana López"))

    transito = guia(c, "Luis Pérez", "64000")
    avanzar(c, transito, "EN_TRANSITO")

    resguardo = guia(c, "María Gómez", "66220")
    avanzar(c, resguardo, "EN_REPARTO")
    for _ in range(2):
        c.entregas().registrar_intento_fallido(resguardo, "Destinatario ausente")

    cancelada = guia(c, "Jorge Díaz", "66220")
    c.envios().cancelar(cancelada)

    express = guia(c, "Sofía Treviño", "01000", nivel="EXPRESS", peso="3")
    avanzar(c, express, "EN_REPARTO")

    print("Datos de demo cargados en", c.config.database_url.split("@")[-1])
    for nombre, n in [("ENTREGADO", entregada), ("EN_TRANSITO", transito),
                      ("EN_RESGUARDO", resguardo), ("CANCELADO", cancelada),
                      ("EXPRESS EN_REPARTO", express)]:
        print(f"  {n}  ->  {nombre}")
    print("Teléfono del remitente para el historial: 8112345678")


if __name__ == "__main__":
    main()
