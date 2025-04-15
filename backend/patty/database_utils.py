from typing import Annotated, Any, Iterable, TypeVar, cast
import datetime
import unittest

from fastapi import Depends, Request
import sqlalchemy.exc
import sqlalchemy.orm

from . import settings


Engine = sqlalchemy.Engine

Session = sqlalchemy.orm.Session


def create_engine(url: str) -> Engine:
    return sqlalchemy.create_engine(url)


def make_session(engine: Engine) -> Session:
    return Session(engine)


class OrmBase(sqlalchemy.orm.DeclarativeBase):
    metadata = sqlalchemy.MetaData(
        naming_convention=dict(
            ix="ix_%(column_0_N_label)s",
            uq="uq_%(table_name)s_%(column_0_N_name)s",
            ck="ck_%(table_name)s_%(constraint_name)s",
            fk="fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            pk="pk_%(table_name)s",
        )
    )


def truncate_all_tables(session: Session) -> None:
    for table in reversed(OrmBase.metadata.sorted_tables):
        try:
            session.execute(table.delete())
            session.execute(sqlalchemy.text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1"))
        except sqlalchemy.exc.ProgrammingError:
            # E.g. when the table does not exist yet
            session.rollback()
        else:
            session.commit()


def _db_engine_dependable(request: Request) -> Engine:
    engine = request.app.extra["database_engine"]
    if not isinstance(engine, Engine):
        raise TypeError(f"Expected an instance of sqlalchemy.Engine, got {type(engine)}")
    return engine


EngineDependable = Annotated[Engine, Depends(_db_engine_dependable)]


def _session_dependable(engine: EngineDependable) -> Iterable[Session]:
    with Session(engine) as session:
        try:
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()


SessionDependable = Annotated[Session, Depends(_session_dependable)]


class TestCaseWithDatabase(unittest.TestCase):
    Model = TypeVar("Model", bound=sqlalchemy.orm.DeclarativeBase)

    __database_url: str
    __database_engine: Engine

    @classmethod
    def setUpClass(cls) -> None:
        import sqlalchemy_utils.functions
        from . import orm_models  # To populate the metadata

        super().setUpClass()
        cls.__database_url = (
            f"{settings.DATABASE_URL}-{cls.__name__}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        sqlalchemy_utils.functions.create_database(cls.__database_url)
        cls.__database_engine = create_engine(cls.__database_url)
        OrmBase.metadata.create_all(cls.__database_engine)

    @classmethod
    def tearDownClass(cls) -> None:
        import sqlalchemy_utils.functions

        cls.__database_engine.dispose()
        sqlalchemy_utils.functions.drop_database(cls.__database_url)
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.session = make_session(self.__database_engine)

    def tearDown(self) -> None:
        self.session.close()
        super().tearDown()

    def create_model(self, __model: type[Model], **kwargs: Any) -> Model:
        instance = __model(**kwargs)
        self.session.add(instance)
        self.session.flush()
        return instance
