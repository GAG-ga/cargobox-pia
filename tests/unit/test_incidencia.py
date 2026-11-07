from datetime import UTC, datetime

import pytest

from src.domain.errores import DatoInvalido, EvidenciaIncompleta, ResolucionInvalida
from src.domain.incidencia import EstadoIncidencia, Incidencia, Resolucion

AHORA = datetime(2026, 11, 5, tzinfo=UTC)


def test_folio_invalido():
    with pytest.raises(DatoInvalido):
        Incidencia.abrir_alerta_retraso("X-1", "CBX-000001", AHORA)


def test_alerta_se_escala_y_se_atiende():
    inc = Incidencia.abrir_alerta_retraso("INC-000001", "CBX-000001", AHORA)
    assert inc.asignada_a == "Atención al Cliente"
    inc.escalar(AHORA)
    assert inc.estado == EstadoIncidencia.ESCALADA
    assert inc.asignada_a == "Supervisor de operaciones"
    inc.resolver(Resolucion.ATENDIDA)
    assert inc.estado == EstadoIncidencia.RESUELTA
    assert [type(e).__name__ for e in inc.extraer_eventos_dominio()] == [
        "AlertaGenerada", "IncidenciaEscalada"]


def test_folio_dano_requiere_foto():
    with pytest.raises(EvidenciaIncompleta):
        Incidencia.abrir_folio_dano("INC-000002", "CBX-000001", "", "Sucursal Centro", AHORA)


def test_resolucion_invalida_para_dano_y_doble_resolucion():
    inc = Incidencia.abrir_folio_dano("INC-000002", "CBX-000001", "d.jpg", "Sucursal Centro", AHORA)
    with pytest.raises(ResolucionInvalida):
        inc.resolver(Resolucion.ATENDIDA)
    inc.resolver(Resolucion.REPOSICION)
    with pytest.raises(ResolucionInvalida):
        inc.resolver(Resolucion.REEMBOLSO)
