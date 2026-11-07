from src.application.puertos import UnitOfWork
from src.infrastructure.repositorios_sql import SqlGuiaRepository, SqlIncidenciaRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Una sesión de base de datos por caso de uso; rollback automático ante errores."""

    def __init__(self, fabrica_sesiones):
        self.fabrica_sesiones = fabrica_sesiones
        self.session = None

    def __enter__(self):
        self.session = self.fabrica_sesiones()
        self.guias = SqlGuiaRepository(self.session)
        self.incidencias = SqlIncidenciaRepository(self.session)
        return self

    def __exit__(self, tipo, valor, traza):
        super().__exit__(tipo, valor, traza)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
