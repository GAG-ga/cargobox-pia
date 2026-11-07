"""US02 y US08 a nivel API, desarrolladas con TDD: estas pruebas se escribieron antes que los
endpoints (RED) y después se implementaron en src/api/rutas/ (GREEN).

    python -m pytest tests/api/test_api_equipo.py -v
"""


# ------------------------------------------------------------ US02 · POST /guias/{numero}/cancelacion
def test_us02_cancelar_guia_recibida(cliente, nueva_guia):
    numero = nueva_guia()
    respuesta = cliente.post(f"/guias/{numero}/cancelacion")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "CANCELADO"
    assert respuesta.json()["mensaje"] == "Este envío fue cancelado en sucursal."


def test_us02_no_se_cancela_guia_clasificada(cliente, nueva_guia, avanzar):
    numero = nueva_guia()
    avanzar(numero, "CLASIFICADO")
    respuesta = cliente.post(f"/guias/{numero}/cancelacion")
    assert respuesta.status_code == 409
    assert respuesta.json()["error"] == "CancelacionNoPermitida"


def test_us02_cancelar_guia_inexistente(cliente):
    respuesta = cliente.post("/guias/CBX-999999/cancelacion")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"] == "GuiaNoEncontrada"


# ------------------------------------------------------------ US08 · GET /rastreo/{numero}
def test_us08_destinatario_ve_estado_fecha_y_mensaje(cliente, nueva_guia, avanzar):
    numero = nueva_guia()
    avanzar(numero, "EN_TRANSITO")
    respuesta = cliente.get(f"/rastreo/{numero}")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["estado"] == "EN_TRANSITO"
    assert datos["fecha_estimada"]
    assert datos["mensaje"] == "Tu paquete va en camino hacia la ciudad de destino."
    assert "eventos" not in datos  # RN-12: sin historial interno


def test_us08_guia_inexistente_mensaje_entendible(cliente):
    respuesta = cliente.get("/rastreo/CBX-999999")
    assert respuesta.status_code == 404
    assert "No encontramos" in respuesta.json()["mensaje"]
