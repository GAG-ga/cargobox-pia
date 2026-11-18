"""El dashboard en HTML se sirve desde la misma API y puede llamarla desde otro origen."""


def test_panel_se_sirve_en_ruta_panel(cliente):
    respuesta = cliente.get("/panel/")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]
    assert "CargoBox" in respuesta.text


def test_cors_permite_llamar_la_api_desde_el_panel(cliente):
    respuesta = cliente.get("/salud", headers={"Origin": "null"})
    assert respuesta.headers["access-control-allow-origin"] == "*"
