"""ADR-007: se prueba la tabla completa de transiciones (permitidas y prohibidas)."""
import itertools

import pytest

from src.domain.errores import TransicionEstadoInvalida
from src.domain.estados import EstadoGuia as E
from src.domain.estados import MaquinaEstadosGuia as M

PERMITIDAS = {
    (E.RECIBIDO, E.CLASIFICADO), (E.RECIBIDO, E.CANCELADO),
    (E.CLASIFICADO, E.EN_TRANSITO),
    (E.EN_TRANSITO, E.CENTRO_DESTINO), (E.EN_TRANSITO, E.PERDIDO),
    (E.CENTRO_DESTINO, E.EN_REPARTO), (E.CENTRO_DESTINO, E.PERDIDO),
    (E.EN_REPARTO, E.ENTREGADO), (E.EN_REPARTO, E.EN_RESGUARDO), (E.EN_REPARTO, E.PERDIDO),
    (E.EN_RESGUARDO, E.EN_REPARTO), (E.EN_RESGUARDO, E.ENTREGADO), (E.EN_RESGUARDO, E.DEVUELTO),
}


@pytest.mark.parametrize("origen, destino", list(itertools.product(E, E)))
def test_tabla_de_transiciones(origen, destino):
    if (origen, destino) in PERMITIDAS:
        assert M.puede(origen, destino)
        assert M.validar(origen, destino)
    else:
        assert not M.puede(origen, destino)
        with pytest.raises(TransicionEstadoInvalida):
            M.validar(origen, destino)


def test_estados_finales():
    assert {e for e in E if M.es_final(e)} == {E.ENTREGADO, E.DEVUELTO, E.CANCELADO, E.PERDIDO}
    assert M.INICIAL == E.RECIBIDO
