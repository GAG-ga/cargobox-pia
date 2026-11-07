"""Application Services (ADR-005): un método por caso de uso; solo coordinan.

Patrón de cada comando: abrir UoW → obtener agregado → invocar UN método de negocio →
guardar y commit → publicar eventos → devolver DTO.
"""
from decimal import Decimal

from src.application.comandos import (
    CambiarDireccionCommand,
    CapturarEvidenciaCommand,
    RegistrarEscaneoCommand,
    RegistrarGuiaCommand,
)
from src.application.dtos import GuiaDTO, IncidenciaDTO, ResumenMonitoreoDTO
from src.application.errores import AccesoDenegado, GuiaNoEncontrada, IncidenciaNoEncontrada
from src.application.mensajes import mensaje_para
from src.application.puertos import (
    AlmacenEvidencias,
    HistorialRastreoReader,
    PublicadorEventos,
    Reloj,
    UnitOfWork,
)
from src.domain.cotizador import Cotizador
from src.domain.especificaciones import (
    ESTADOS_EN_SEGUIMIENTO,
    DebeEscalarse,
    RequiereAlertaPorRetraso,
    ResguardoVencido,
)
from src.domain.estados import EstadoGuia
from src.domain.guia import Guia
from src.domain.incidencia import Incidencia, Resolucion, TipoIncidencia
from src.domain.value_objects import (
    Dimensiones,
    Dinero,
    Direccion,
    EvidenciaEntrega,
    NivelServicio,
    Paquete,
    Persona,
    Peso,
)


def a_dto(g: Guia) -> GuiaDTO:
    return GuiaDTO(
        numero=g.numero.valor, estado=g.estado.value, nivel=g.nivel.value,
        tarifa=str(g.tarifa.monto), fecha_estimada=g.fecha_estimada,
        destino=f"{g.destino.calle}, CP {g.destino.codigo_postal}",
        intentos_fallidos=g.intentos_fallidos, con_garantia=g.con_garantia,
        cargos_adicionales=str(g.cargos_adicionales.monto), reembolso=str(g.reembolso.monto),
        compensacion=str(g.compensacion.monto), mensaje=mensaje_para(g.estado))


def a_dto_incidencia(i: Incidencia) -> IncidenciaDTO:
    return IncidenciaDTO(i.folio, i.numero_guia, i.tipo.value, i.estado.value, i.asignada_a,
                         i.resolucion.value if i.resolucion else None)


class _ServicioBase:
    def __init__(self, uow: UnitOfWork, publicador: PublicadorEventos, reloj: Reloj):
        self.uow, self.publicador, self.reloj = uow, publicador, reloj

    def _obtener(self, numero: str) -> Guia:
        guia = self.uow.guias.por_numero(numero)
        if guia is None:
            raise GuiaNoEncontrada(numero)
        return guia

    def _guardar_y_publicar(self, *agregados) -> None:
        for a in agregados:
            (self.uow.guias if isinstance(a, Guia) else self.uow.incidencias).guardar(a)
        self.uow.commit()
        eventos = [e for a in agregados for e in a.extraer_eventos_dominio()]
        self.publicador.publicar(eventos)


class EnvioApplicationService(_ServicioBase):
    def __init__(self, uow, publicador, reloj, cotizador: Cotizador | None = None):
        super().__init__(uow, publicador, reloj)
        self.cotizador = cotizador or Cotizador()

    def registrar_guia(self, cmd: RegistrarGuiaCommand) -> GuiaDTO:  # US01
        with self.uow:
            paquete = Paquete(Peso(cmd.peso_kg), Dimensiones(cmd.largo_cm, cmd.ancho_cm, cmd.alto_cm))
            origen = Direccion(cmd.origen_calle, cmd.origen_cp)
            destino = Direccion(cmd.destino_calle, cmd.destino_cp)
            nivel = NivelServicio(cmd.nivel)
            tarifa = self.cotizador.cotizar(paquete, origen, destino, nivel)
            guia = Guia.generar(
                self.uow.guias.siguiente_numero(),
                Persona(cmd.remitente_nombre, cmd.remitente_telefono),
                Persona(cmd.destinatario_nombre, cmd.destinatario_telefono),
                origen, destino, paquete, nivel, Dinero(Decimal(str(cmd.valor_declarado))),
                tarifa, cmd.sucursal, self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)

    def cancelar(self, numero: str) -> GuiaDTO:  # US02
        with self.uow:
            guia = self._obtener(numero)
            guia.cancelar(self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)

    def corregir_datos(self, numero: str, origen: tuple[str, str] | None = None,
                       destino: tuple[str, str] | None = None) -> GuiaDTO:  # US03
        with self.uow:
            guia = self._obtener(numero)
            guia.corregir_datos(Direccion(*origen) if origen else None,
                                Direccion(*destino) if destino else None)
            self._guardar_y_publicar(guia)
            return a_dto(guia)

    def cambiar_direccion(self, cmd: CambiarDireccionCommand) -> GuiaDTO:  # US11
        with self.uow:
            guia = self._obtener(cmd.numero_guia)
            guia.cambiar_direccion(Direccion(cmd.calle, cmd.codigo_postal),
                                   cmd.identidad_validada, self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)


class RastreoApplicationService(_ServicioBase):
    def registrar_escaneo(self, cmd: RegistrarEscaneoCommand) -> GuiaDTO:  # US04
        with self.uow:
            guia = self._obtener(cmd.numero_guia)
            guia.registrar_escaneo(EstadoGuia(cmd.nuevo_estado), cmd.ubicacion, self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)


class EntregaApplicationService(_ServicioBase):
    def __init__(self, uow, publicador, reloj, almacen: AlmacenEvidencias):
        super().__init__(uow, publicador, reloj)
        self.almacen = almacen

    def registrar_intento_fallido(self, numero: str, motivo: str,
                                  ubicacion: str = "Domicilio del destinatario") -> GuiaDTO:  # US05
        with self.uow:
            guia = self._obtener(numero)
            guia.registrar_intento_fallido(motivo, ubicacion, self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)

    def capturar_evidencia_entrega(self, cmd: CapturarEvidenciaCommand) -> GuiaDTO:  # US06/07/10
        evidencia = EvidenciaEntrega(cmd.firma_digital, cmd.foto, cmd.nombre_receptor,
                                     cmd.es_tercero)  # RN-07 antes de tocar el almacén
        with self.uow:
            guia = self._obtener(cmd.numero_guia)
            self.almacen.guardar(guia.numero.valor, cmd.firma_digital, cmd.foto)
            guia.registrar_entrega(evidencia, cmd.ubicacion, self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)

    def reagendar(self, numero: str) -> GuiaDTO:  # US10
        with self.uow:
            guia = self._obtener(numero)
            guia.reagendar(self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)


class IncidenciaApplicationService(_ServicioBase):
    def monitorear_retrasos(self) -> list[str]:  # US12 / RN-15
        ahora = self.reloj.ahora()
        with self.uow:
            con_alerta = {i.numero_guia for i in self.uow.incidencias.abiertas(TipoIncidencia.RETRASO)}
            spec = RequiereAlertaPorRetraso(ahora)
            nuevas = []
            for guia in self.uow.guias.en_estados(set(ESTADOS_EN_SEGUIMIENTO)):
                if spec.es_satisfecha_por(guia) and guia.numero.valor not in con_alerta:
                    inc = Incidencia.abrir_alerta_retraso(
                        self.uow.incidencias.siguiente_folio(), guia.numero.valor, ahora)
                    self.uow.incidencias.guardar(inc)
                    nuevas.append(inc)
            self.uow.commit()
            self.publicador.publicar([e for i in nuevas for e in i.extraer_eventos_dominio()])
            return [i.folio for i in nuevas]

    def escalar_alertas(self) -> list[str]:  # US13 / RN-16
        ahora = self.reloj.ahora()
        with self.uow:
            spec = DebeEscalarse(ahora)
            escaladas = [i for i in self.uow.incidencias.abiertas(TipoIncidencia.RETRASO)
                         if spec.es_satisfecha_por(i)]
            for inc in escaladas:
                inc.escalar(ahora)
                self.uow.incidencias.guardar(inc)
            self.uow.commit()
            self.publicador.publicar([e for i in escaladas for e in i.extraer_eventos_dominio()])
            return [i.folio for i in escaladas]

    def vencer_resguardos(self) -> list[str]:  # US10 / RN-13
        ahora = self.reloj.ahora()
        with self.uow:
            spec = ResguardoVencido(ahora)
            vencidas = [g for g in self.uow.guias.en_estados({EstadoGuia.EN_RESGUARDO})
                        if spec.es_satisfecha_por(g)]
            for guia in vencidas:
                guia.devolver(ahora)
                self.uow.guias.guardar(guia)
            self.uow.commit()
            self.publicador.publicar([e for g in vencidas for e in g.extraer_eventos_dominio()])
            return [g.numero.valor for g in vencidas]

    def ejecutar_monitoreo(self) -> ResumenMonitoreoDTO:  # ADR-011
        return ResumenMonitoreoDTO(self.monitorear_retrasos(), self.escalar_alertas(),
                                   self.vencer_resguardos())

    def listar_pendientes(self) -> list[IncidenciaDTO]:  # US12 / US13: alertas visibles
        with self.uow:
            return [a_dto_incidencia(i) for i in self.uow.incidencias.pendientes()]

    def abrir_folio_dano(self, numero: str, foto: str) -> IncidenciaDTO:  # US14 / RN-17
        with self.uow:
            guia = self._obtener(numero)
            inc = Incidencia.abrir_folio_dano(self.uow.incidencias.siguiente_folio(),
                                              guia.numero.valor, foto, guia.sucursal_origen,
                                              self.reloj.ahora())
            self._guardar_y_publicar(inc)
            return a_dto_incidencia(inc)

    def resolver(self, folio: str, resolucion: str) -> IncidenciaDTO:  # US14
        with self.uow:
            inc = self.uow.incidencias.por_folio(folio)
            if inc is None:
                raise IncidenciaNoEncontrada(folio)
            inc.resolver(Resolucion(resolucion))
            self._guardar_y_publicar(inc)
            return a_dto_incidencia(inc)

    def declarar_perdida(self, numero: str) -> GuiaDTO:  # US15 / RN-18
        with self.uow:
            guia = self._obtener(numero)
            guia.declarar_perdida(self.reloj.ahora())
            self._guardar_y_publicar(guia)
            return a_dto(guia)


class ConsultaRastreoQueryService:
    """Lado de lectura (CQRS): no carga el agregado ni abre transacción de escritura."""

    def __init__(self, lector: HistorialRastreoReader):
        self.lector = lector

    def estado_publico(self, numero: str) -> dict:  # US08 / RN-12
        vista = self.lector.estado_publico(numero)
        if vista is None:
            raise GuiaNoEncontrada(numero)
        return {**vista, "mensaje": mensaje_para(EstadoGuia(vista["estado"]))}

    def historial(self, numero: str, telefono_remitente: str) -> dict:  # US09 / RN-08
        vista = self.lector.historial(numero)
        if vista is None:
            raise GuiaNoEncontrada(numero)
        if vista.pop("telefono_remitente") != telefono_remitente:
            raise AccesoDenegado()
        return vista
