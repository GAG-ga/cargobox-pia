from datetime import UTC, datetime

import pytest

from src.application.puertos import RelojSistema
from src.domain.errores import TransicionEstadoInvalida


def test_no_se_devuelve_antes_de_vencer_el_resguardo(sistema):
    n = sistema.registrar().numero
    sistema.avanzar_hasta(n, "EN_REPARTO")
    for _ in range(2):
        sistema.entregas.registrar_intento_fallido(n, "ausente")
    with pytest.raises(TransicionEstadoInvalida):
        sistema.guia(n).devolver(sistema.reloj.ahora())


def test_reloj_del_sistema_usa_utc():
    assert RelojSistema().ahora().tzinfo == UTC
    assert RelojSistema().ahora() <= datetime.now(UTC)
