"""Modelos ORM (tablas). Son distintos de las entidades del dominio: el repositorio traduce."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SecuenciaModel(Base):
    """Contadores para números de guía y folios (RN-02)."""

    __tablename__ = "secuencias"
    nombre: Mapped[str] = mapped_column(String(20), primary_key=True)
    valor: Mapped[int] = mapped_column(Integer, default=0)


class GuiaModel(Base):
    __tablename__ = "guias"
    numero: Mapped[str] = mapped_column(String(10), primary_key=True)  # único por diseño
    remitente_nombre: Mapped[str] = mapped_column(String(120))
    remitente_telefono: Mapped[str] = mapped_column(String(10))
    destinatario_nombre: Mapped[str] = mapped_column(String(120))
    destinatario_telefono: Mapped[str] = mapped_column(String(10))
    origen_calle: Mapped[str] = mapped_column(String(200))
    origen_cp: Mapped[str] = mapped_column(String(5))
    destino_calle: Mapped[str] = mapped_column(String(200))
    destino_cp: Mapped[str] = mapped_column(String(5))
    peso_kg: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    largo_cm: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    ancho_cm: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    alto_cm: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    nivel: Mapped[str] = mapped_column(String(10))
    valor_declarado: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    tarifa: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    sucursal_origen: Mapped[str] = mapped_column(String(120))
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_estimada: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), index=True)
    con_garantia: Mapped[bool] = mapped_column(Boolean, default=True)
    reagendada: Mapped[bool] = mapped_column(Boolean, default=False)
    resguardo_desde: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cargos_adicionales: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    reembolso: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    compensacion: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    evidencia_firma: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidencia_foto: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidencia_receptor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    evidencia_es_tercero: Mapped[bool] = mapped_column(Boolean, default=False)
    eventos: Mapped[list["EventoRastreoModel"]] = relationship(
        cascade="all, delete-orphan", order_by="EventoRastreoModel.orden")
    intentos: Mapped[list["IntentoEntregaModel"]] = relationship(
        cascade="all, delete-orphan", order_by="IntentoEntregaModel.numero")


class EventoRastreoModel(Base):
    __tablename__ = "eventos_rastreo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_guia: Mapped[str] = mapped_column(ForeignKey("guias.numero"), index=True)
    orden: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(20))
    ubicacion: Mapped[str] = mapped_column(String(200))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IntentoEntregaModel(Base):
    __tablename__ = "intentos_entrega"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_guia: Mapped[str] = mapped_column(ForeignKey("guias.numero"), index=True)
    numero: Mapped[int] = mapped_column(Integer)
    exitoso: Mapped[bool] = mapped_column(Boolean)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    motivo: Mapped[str] = mapped_column(String(200), default="")


class IncidenciaModel(Base):
    __tablename__ = "incidencias"
    folio: Mapped[str] = mapped_column(String(10), primary_key=True)
    numero_guia: Mapped[str] = mapped_column(ForeignKey("guias.numero"), index=True)
    tipo: Mapped[str] = mapped_column(String(10))
    estado: Mapped[str] = mapped_column(String(10), index=True)
    abierta_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    asignada_a: Mapped[str] = mapped_column(String(120))
    evidencia_foto: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resolucion: Mapped[str | None] = mapped_column(String(12), nullable=True)
