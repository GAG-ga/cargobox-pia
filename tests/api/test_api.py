"""Pruebas de integración de la API completa (HTTP → servicios → SQL)."""
import pytest

from tests.api.conftest import GUIA

ENTREGA = {"firma_digital": "firma.png", "foto": "foto.jpg", "nombre_receptor": "Ana López"}


def test_salud_y_redireccion_a_swagger(cliente):
    assert cliente.get("/salud").json()["estado"] == "ok"
    assert cliente.get("/", follow_redirects=False).headers["location"] == "/docs"
    assert "CargoBox API" in cliente.get("/openapi.json").json()["info"]["title"]


def test_us01_registrar_guia(cliente):
    r = cliente.post("/guias", json=GUIA)
    assert r.status_code == 201
    assert (r.json()["numero"], r.json()["tarifa"]) == ("CBX-000001", "249.00")


def test_us01_carga_especial_mensaje_para_el_cliente(cliente):
    r = cliente.post("/guias", json={**GUIA, "paquete": {**GUIA["paquete"], "peso_kg": 31}})
    assert r.status_code == 422
    assert r.json()["error"] == "CargaEspecialRequerida"
    assert "carga especial" in r.json()["mensaje"]


def test_datos_incompletos_mensaje_en_espanol(cliente):
    r = cliente.post("/guias", json={"nivel": "ESTANDAR"})
    assert r.status_code == 422
    assert r.json()["error"] == "DatosIncompletos"
    assert "remitente" in r.json()["mensaje"]


def test_dato_invalido_telefono(cliente):
    r = cliente.post("/guias", json={**GUIA, "remitente": {"nombre": "Carlos", "telefono": "123"}})
    assert r.status_code == 422
    assert r.json()["mensaje"] == "El teléfono debe tener 10 dígitos."


def test_us03_corregir_destino(cliente, nueva_guia):
    n = nueva_guia()
    r = cliente.patch(f"/guias/{n}/datos", json={"destino": {"calle": "Calle Roble 12",
                                                               "codigo_postal": "66220"}})
    assert r.json()["destino"] == "Calle Roble 12, CP 66220"
    r = cliente.patch(f"/guias/{n}/datos", json={"origen": {"calle": "Otra 1", "codigo_postal": "66450"}})
    assert r.status_code == 200


def test_us04_escaneo_que_salta_estado(cliente, nueva_guia):
    n = nueva_guia()
    r = cliente.post(f"/guias/{n}/escaneos", json={"nuevo_estado": "EN_TRANSITO", "ubicacion": "X"})
    assert (r.status_code, r.json()["error"]) == (409, "TransicionEstadoInvalida")


def test_us05_us10_intentos_resguardo_y_reagendar(cliente, nueva_guia, avanzar):
    n = nueva_guia()
    avanzar(n, "EN_REPARTO")
    cliente.post(f"/guias/{n}/intentos-fallidos", json={"motivo": "ausente"})
    r = cliente.post(f"/guias/{n}/intentos-fallidos", json={"motivo": "ausente"})
    assert r.json()["estado"] == "EN_RESGUARDO"
    assert "resguardo" in r.json()["mensaje"]
    r = cliente.post(f"/guias/{n}/intentos-fallidos", json={"motivo": "ausente"})
    assert r.json()["error"] == "LimiteIntentosExcedido"
    assert cliente.post(f"/guias/{n}/reagendamiento").json()["estado"] == "EN_REPARTO"


def test_us06_entrega_con_evidencia_y_us09_historial(cliente, nueva_guia, avanzar):
    n = nueva_guia()
    avanzar(n, "EN_REPARTO")
    r = cliente.post(f"/guias/{n}/entrega", json=ENTREGA)
    assert r.json()["estado"] == "ENTREGADO"
    h = cliente.get(f"/rastreo/{n}/historial", params={"telefono": "8112345678"}).json()
    assert [e["estado"] for e in h["eventos"]] == [
        "RECIBIDO", "CLASIFICADO", "EN_TRANSITO", "CENTRO_DESTINO", "EN_REPARTO", "ENTREGADO"]
    notificaciones = cliente.app.state.contenedor.notificaciones.enviadas
    assert any("entregado" in m for m in notificaciones)


def test_us06_evidencia_incompleta(cliente, nueva_guia, avanzar):
    n = nueva_guia()
    avanzar(n, "EN_REPARTO")
    r = cliente.post(f"/guias/{n}/entrega", json={**ENTREGA, "foto": ""})
    assert (r.status_code, r.json()["error"]) == (422, "EvidenciaIncompleta")


def test_us07_entrega_a_tercero(cliente, nueva_guia, avanzar):
    n = nueva_guia()
    avanzar(n, "EN_REPARTO")
    r = cliente.post(f"/guias/{n}/entrega", json={**ENTREGA, "nombre_receptor": "Portero",
                                                   "es_tercero": True})
    assert r.json()["estado"] == "ENTREGADO"


def test_us09_acceso_denegado(cliente, nueva_guia):
    n = nueva_guia()
    r = cliente.get(f"/rastreo/{n}/historial", params={"telefono": "8100000000"})
    assert (r.status_code, r.json()["error"]) == (403, "AccesoDenegado")


def test_us11_cambio_de_direccion(cliente, nueva_guia, avanzar):
    n = nueva_guia()
    avanzar(n, "EN_TRANSITO")
    datos = {"nueva_direccion": {"calle": "Av. Reforma 500", "codigo_postal": "06600"},
             "identidad_validada": True}
    r = cliente.patch(f"/guias/{n}/direccion", json=datos)
    assert (r.json()["cargos_adicionales"], r.json()["con_garantia"]) == ("80.00", False)
    r = cliente.patch(f"/guias/{n}/direccion", json={**datos, "identidad_validada": False})
    assert (r.status_code, r.json()["error"]) == (422, "IdentidadNoValidada")


def test_us14_folio_de_dano_y_resolucion(cliente, nueva_guia):
    n = nueva_guia()
    r = cliente.post("/incidencias/danos", json={"numero_guia": n, "foto": "dano.jpg"})
    assert r.status_code == 201
    folio = r.json()["folio"]
    r = cliente.post(f"/incidencias/{folio}/resolucion", json={"resolucion": "REPOSICION"})
    assert (r.json()["estado"], r.json()["resolucion"]) == ("RESUELTA", "REPOSICION")
    r = cliente.post("/incidencias/INC-999999/resolucion", json={"resolucion": "REPOSICION"})
    assert r.status_code == 404


def test_us15_declarar_perdida_no_permitida_aun(cliente, nueva_guia, avanzar):
    n = nueva_guia()
    avanzar(n, "EN_TRANSITO")
    r = cliente.post(f"/guias/{n}/perdida")
    assert (r.status_code, r.json()["error"]) == (409, "PerdidaNoDeclarable")


@pytest.mark.parametrize("dias, alertas", [(0, 0), (2, 1)])
def test_monitoreo_con_fecha_simulada(cliente, nueva_guia, dias, alertas):
    from datetime import UTC, datetime, timedelta
    nueva_guia()
    ahora = (datetime.now(UTC) + timedelta(days=dias)).isoformat()
    r = cliente.post("/monitoreo/ejecutar", params={"ahora": ahora})
    assert r.status_code == 200
    assert len(r.json()["alertas_generadas"]) == alertas


def test_us12_us13_alerta_visible_y_escalada(cliente, nueva_guia):
    from datetime import UTC, datetime, timedelta
    n = nueva_guia()
    dentro = lambda h: (datetime.now(UTC) + timedelta(hours=h)).isoformat()  # noqa: E731
    r = cliente.post("/monitoreo/ejecutar", params={"ahora": dentro(25)}).json()
    assert len(r["alertas_generadas"]) == 1
    pendientes = cliente.get("/incidencias").json()
    assert (pendientes[0]["numero_guia"], pendientes[0]["estado"]) == (n, "ABIERTA")
    r = cliente.post("/monitoreo/ejecutar", params={"ahora": dentro(74)}).json()
    assert r["alertas_escaladas"] == [pendientes[0]["folio"]]
    assert cliente.get("/incidencias").json()[0]["asignada_a"] == "Supervisor de operaciones"


def test_monitoreo_sin_fecha_usa_hora_actual(cliente):
    assert cliente.post("/monitoreo/ejecutar").json()["alertas_generadas"] == []
