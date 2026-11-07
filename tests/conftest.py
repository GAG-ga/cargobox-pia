from decimal import Decimal
from unittest.mock import Mock

import pytest

from src.application.comandos import RegistrarEscaneoCommand, RegistrarGuiaCommand
from src.application.servicios import (
    ConsultaRastreoQueryService,
    EntregaApplicationService,
    EnvioApplicationService,
    IncidenciaApplicationService,
    RastreoApplicationService,
)
from tests.fakes import (
    LectorHistorialEnMemoria,
    PublicadorEnMemoria,
    RelojFijo,
    UnitOfWorkEnMemoria,
)

RUTA = [("CLASIFICADO", "CEDIS Monterrey"), ("EN_TRANSITO", "Ruta MTY-CDMX"),
        ("CENTRO_DESTINO", "CEDIS CDMX"), ("EN_REPARTO", "Unidad 12 CDMX")]


def comando_guia(**cambios) -> RegistrarGuiaCommand:
    datos = dict(remitente_nombre="Carlos Ruiz", remitente_telefono="8112345678",
                 destinatario_nombre="Ana López", destinatario_telefono="8187654321",
                 origen_calle="Av. Universidad 100", origen_cp="66450",
                 destino_calle="Calle Roble 10", destino_cp="66220",
                 peso_kg=Decimal("10"), largo_cm=Decimal("40"), ancho_cm=Decimal("30"),
                 alto_cm=Decimal("20"), nivel="ESTANDAR", valor_declarado=Decimal("1200"),
                 sucursal="Sucursal San Nicolás")
    datos.update(cambios)
    return RegistrarGuiaCommand(**datos)


class Sistema:
    """Ensambla los servicios con dobles en memoria, como lo haría api/dependencias.py."""

    def __init__(self):
        self.uow = UnitOfWorkEnMemoria()
        self.reloj = RelojFijo()
        self.publicador = PublicadorEnMemoria()
        self.almacen = Mock()
        self.almacen.guardar.return_value = "evidencias/ref"
        args = (self.uow, self.publicador, self.reloj)
        self.envios = EnvioApplicationService(*args)
        self.rastreo = RastreoApplicationService(*args)
        self.entregas = EntregaApplicationService(*args, self.almacen)
        self.incidencias = IncidenciaApplicationService(*args)
        self.consultas = ConsultaRastreoQueryService(LectorHistorialEnMemoria(self.uow.guias))

    def registrar(self, **cambios):
        return self.envios.registrar_guia(comando_guia(**cambios))

    def avanzar_hasta(self, numero, estado_final):
        for estado, lugar in RUTA:
            self.rastreo.registrar_escaneo(RegistrarEscaneoCommand(numero, estado, lugar))
            if estado == estado_final:
                break

    def guia(self, numero):
        return self.uow.guias.por_numero(numero)


@pytest.fixture
def sistema():
    return Sistema()
