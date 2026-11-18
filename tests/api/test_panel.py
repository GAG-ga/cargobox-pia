"""El dashboard en HTML se sirve desde la misma API y puede llamarla desde otro origen."""


def test_panel_se_sirve_en_ruta_panel(cliente):
    respuesta = cliente.get("/panel/")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]
    assert "CargoBox" in respuesta.text


def test_cors_permite_llamar_la_api_desde_el_panel(cliente):
    respuesta = cliente.get("/salud", headers={"Origin": "null"})
    assert respuesta.headers["access-control-allow-origin"] == "*"


def _estados_de_operacion(html: str, op: str) -> set[str]:
    import re

    encontrado = re.search(rf'data-op="{op}" data-estados="([A-Z_,]+)"', html)
    assert encontrado, f"El panel no tiene la operación {op}"
    return set(encontrado.group(1).split(","))


def test_panel_ofrece_cada_operacion_solo_en_los_estados_que_permiten_las_reglas(cliente):
    """El panel no debe mostrar operaciones que la API siempre rechazaría (RN-09, RN-10, RN-14, RN-18)."""
    from src.domain.especificaciones import PermiteCambioDireccion, PermiteCorreccion, PuedeCancelarse
    from src.domain.estados import EstadoGuia as E

    html = cliente.get("/panel/").text
    esperado = {
        "cancelar": PuedeCancelarse().estados,
        "corregir": PermiteCorreccion().estados,
        "cambio-direccion": PermiteCambioDireccion().estados,
        "perdida": {E.EN_TRANSITO, E.CENTRO_DESTINO, E.EN_REPARTO},
    }
    for op, estados in esperado.items():
        assert _estados_de_operacion(html, op) == {e.value for e in estados}, op
