"""US13 — docs/gherkin/US13_escalamiento.feature (RN-16)."""


def alerta_abierta(sistema):
    sistema.registrar()
    sistema.reloj.avanzar(hours=24)
    return sistema.incidencias.monitorear_retrasos()[0]


def test_alerta_con_48_horas_se_escala(sistema):
    folio = alerta_abierta(sistema)
    sistema.reloj.avanzar(hours=48)
    assert sistema.incidencias.escalar_alertas() == [folio]
    inc = sistema.uow.incidencias.por_folio(folio)
    assert (inc.estado.value, inc.asignada_a) == ("ESCALADA", "Supervisor de operaciones")


def test_alertas_pendientes_visibles_para_supervisor(sistema):
    folio = alerta_abierta(sistema)
    sistema.reloj.avanzar(hours=48)
    sistema.incidencias.escalar_alertas()
    pendientes = sistema.incidencias.listar_pendientes()
    assert [(i.folio, i.estado) for i in pendientes] == [(folio, "ESCALADA")]


def test_alerta_con_47_horas_no_se_escala(sistema):
    folio = alerta_abierta(sistema)
    sistema.reloj.avanzar(hours=47)
    assert sistema.incidencias.escalar_alertas() == []
    assert sistema.uow.incidencias.por_folio(folio).estado.value == "ABIERTA"


def test_monitoreo_completo_en_una_llamada(sistema):
    alerta_abierta(sistema)
    sistema.reloj.avanzar(hours=48)
    resumen = sistema.incidencias.ejecutar_monitoreo()
    assert resumen.alertas_escaladas and resumen.guias_devueltas == []
