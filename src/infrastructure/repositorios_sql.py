"""Repositorios SQLAlchemy: traducen entre el agregado del dominio y las tablas."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.estados import EstadoGuia
from src.domain.guia import EventoRastreo, Guia, IntentoEntrega
from src.domain.incidencia import (
    EstadoIncidencia,
    Incidencia,
    Resolucion,
    TipoIncidencia,
)
from src.domain.value_objects import (
    Dimensiones,
    Dinero,
    Direccion,
    EvidenciaEntrega,
    NivelServicio,
    NumeroGuia,
    Paquete,
    Persona,
    Peso,
)
from src.infrastructure.db import como_utc
from src.infrastructure.modelos import (
    EventoRastreoModel,
    GuiaModel,
    IncidenciaModel,
    IntentoEntregaModel,
    SecuenciaModel,
)


def _siguiente(session: Session, nombre: str) -> int:
    fila = session.scalar(select(SecuenciaModel).where(SecuenciaModel.nombre == nombre)
                          .with_for_update())
    if fila is None:
        fila = SecuenciaModel(nombre=nombre, valor=0)
        session.add(fila)
    fila.valor += 1
    session.flush()
    return fila.valor


class SqlGuiaRepository:
    def __init__(self, session: Session):
        self.session = session

    def siguiente_numero(self) -> NumeroGuia:
        return NumeroGuia.desde_secuencia(_siguiente(self.session, "guia"))

    def por_numero(self, numero: str) -> Guia | None:
        modelo = self.session.get(GuiaModel, numero)
        return self._a_dominio(modelo) if modelo else None

    def en_estados(self, estados: set[EstadoGuia]) -> list[Guia]:
        filas = self.session.scalars(select(GuiaModel).where(
            GuiaModel.estado.in_([e.value for e in estados])))
        return [self._a_dominio(m) for m in filas]

    def guardar(self, g: Guia) -> None:
        m = self.session.get(GuiaModel, g.numero.valor) or GuiaModel(numero=g.numero.valor)
        m.remitente_nombre, m.remitente_telefono = g.remitente.nombre, g.remitente.telefono
        m.destinatario_nombre, m.destinatario_telefono = g.destinatario.nombre, g.destinatario.telefono
        m.origen_calle, m.origen_cp = g.origen.calle, g.origen.codigo_postal
        m.destino_calle, m.destino_cp = g.destino.calle, g.destino.codigo_postal
        dims = g.paquete.dimensiones
        m.peso_kg, m.largo_cm, m.ancho_cm, m.alto_cm = (
            g.paquete.peso.kg, dims.largo_cm, dims.ancho_cm, dims.alto_cm)
        m.nivel, m.valor_declarado, m.tarifa = g.nivel.value, g.valor_declarado.monto, g.tarifa.monto
        m.sucursal_origen, m.creada_en, m.fecha_estimada = g.sucursal_origen, g.creada_en, g.fecha_estimada
        m.estado, m.con_garantia, m.reagendada = g.estado.value, g.con_garantia, g.reagendada
        m.resguardo_desde = g.resguardo_desde
        m.cargos_adicionales, m.reembolso = g.cargos_adicionales.monto, g.reembolso.monto
        m.compensacion = g.compensacion.monto
        ev = g.evidencia
        m.evidencia_firma = ev.firma_digital if ev else None
        m.evidencia_foto = ev.foto if ev else None
        m.evidencia_receptor = ev.nombre_receptor if ev else None
        m.evidencia_es_tercero = ev.es_tercero if ev else False
        # El historial solo crece: se agregan los eventos e intentos nuevos.
        for i, e in enumerate(g.eventos[len(m.eventos):], start=len(m.eventos)):
            m.eventos.append(EventoRastreoModel(orden=i, estado=e.estado.value,
                                                ubicacion=e.ubicacion, fecha_hora=e.fecha_hora))
        for it in g.intentos[len(m.intentos):]:
            m.intentos.append(IntentoEntregaModel(numero=it.numero, exitoso=it.exitoso,
                                                  fecha_hora=it.fecha_hora, motivo=it.motivo))
        self.session.add(m)
        self.session.flush()

    @staticmethod
    def _a_dominio(m: GuiaModel) -> Guia:
        evidencia = (EvidenciaEntrega(m.evidencia_firma, m.evidencia_foto, m.evidencia_receptor,
                                      m.evidencia_es_tercero) if m.evidencia_firma else None)
        return Guia(
            numero=NumeroGuia(m.numero),
            remitente=Persona(m.remitente_nombre, m.remitente_telefono),
            destinatario=Persona(m.destinatario_nombre, m.destinatario_telefono),
            origen=Direccion(m.origen_calle, m.origen_cp),
            destino=Direccion(m.destino_calle, m.destino_cp),
            paquete=Paquete(Peso(m.peso_kg), Dimensiones(m.largo_cm, m.ancho_cm, m.alto_cm)),
            nivel=NivelServicio(m.nivel), valor_declarado=Dinero(m.valor_declarado),
            tarifa=Dinero(m.tarifa), sucursal_origen=m.sucursal_origen,
            creada_en=como_utc(m.creada_en), fecha_estimada=m.fecha_estimada,
            estado=EstadoGuia(m.estado),
            eventos=[EventoRastreo(EstadoGuia(e.estado), e.ubicacion, como_utc(e.fecha_hora))
                     for e in m.eventos],
            intentos=[IntentoEntrega(i.numero, i.exitoso, como_utc(i.fecha_hora), i.motivo)
                      for i in m.intentos],
            evidencia=evidencia, con_garantia=m.con_garantia, reagendada=m.reagendada,
            resguardo_desde=como_utc(m.resguardo_desde),
            cargos_adicionales=Dinero(m.cargos_adicionales), reembolso=Dinero(m.reembolso),
            compensacion=Dinero(m.compensacion))


class SqlIncidenciaRepository:
    def __init__(self, session: Session):
        self.session = session

    def siguiente_folio(self) -> str:
        return Incidencia.folio_desde_secuencia(_siguiente(self.session, "incidencia"))

    def por_folio(self, folio: str) -> Incidencia | None:
        m = self.session.get(IncidenciaModel, folio)
        return self._a_dominio(m) if m else None

    def abiertas(self, tipo: TipoIncidencia | None = None) -> list[Incidencia]:
        consulta = select(IncidenciaModel).where(IncidenciaModel.estado == EstadoIncidencia.ABIERTA.value)
        if tipo is not None:
            consulta = consulta.where(IncidenciaModel.tipo == tipo.value)
        return [self._a_dominio(m) for m in self.session.scalars(consulta)]

    def pendientes(self) -> list[Incidencia]:
        consulta = (select(IncidenciaModel)
                    .where(IncidenciaModel.estado != EstadoIncidencia.RESUELTA.value)
                    .order_by(IncidenciaModel.folio))
        return [self._a_dominio(m) for m in self.session.scalars(consulta)]

    def guardar(self, i: Incidencia) -> None:
        m = self.session.get(IncidenciaModel, i.folio) or IncidenciaModel(folio=i.folio)
        m.numero_guia, m.tipo, m.estado = i.numero_guia, i.tipo.value, i.estado.value
        m.abierta_en, m.asignada_a, m.evidencia_foto = i.abierta_en, i.asignada_a, i.evidencia_foto
        m.resolucion = i.resolucion.value if i.resolucion else None
        self.session.add(m)
        self.session.flush()

    @staticmethod
    def _a_dominio(m: IncidenciaModel) -> Incidencia:
        return Incidencia(m.folio, m.numero_guia, TipoIncidencia(m.tipo), como_utc(m.abierta_en),
                          m.asignada_a, EstadoIncidencia(m.estado), m.evidencia_foto,
                          Resolucion(m.resolucion) if m.resolucion else None)
