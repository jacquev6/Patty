from typing import Annotated, Any, Iterable, TypeVar
import contextlib
import datetime
import os
import typing
import unittest

from fastapi import Depends, Request
import alembic.command
import alembic.config
import psycopg2
import sqlalchemy as sql
import sqlalchemy.exc
import sqlalchemy.orm

from . import settings

Engine = sqlalchemy.Engine

Session = sqlalchemy.orm.Session


def create_engine(url: str, echo: bool = False) -> Engine:
    return sqlalchemy.create_engine(url, echo=echo)


def make_session(engine: Engine) -> Session:
    return Session(engine)


# Custom collation: https://dba.stackexchange.com/a/285230
create_exercise_number_collation = sql.text(
    "CREATE COLLATION exercise_number (provider = icu, locale = 'en-u-kn-true')"
)


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
    session.execute(OrmBase.metadata.tables["exercise_classes"].update().values(latest_strategy_settings_id=None))

    for table in reversed(OrmBase.metadata.sorted_tables):
        try:
            with session.begin_nested():
                session.execute(table.delete())
        except sqlalchemy.exc.ProgrammingError:
            # E.g. when the table does not exist yet
            pass

        try:
            with session.begin_nested():
                session.execute(sqlalchemy.text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1"))
        except sqlalchemy.exc.ProgrammingError:
            # E.g. when the table has no auto-incremented ID
            pass


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
    engine: Engine

    @classmethod
    def setUpClass(cls) -> None:
        import sqlalchemy_utils.functions

        super().setUpClass()
        cls.__database_url = (
            f"{settings.DATABASE_URL}-{cls.__name__}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        sqlalchemy_utils.functions.create_database(cls.__database_url)
        cls.engine = create_engine(cls.__database_url)

        # Creating the DB using Alembic by default is very important:
        # It lets us test that the migrations produce the DB we expect.
        # The alternative, using 'OrmBase.metadata.create_all', always produces exactly the DB described
        # by the ORM models, but migrations could diverge from that.
        # One concrete example is the 'CheckConstraint' on the 'Input' model: it was not picked up by the migration.
        # (Documented: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).
        # So the unit test for this constraint was passing using 'OrmBase.metadata.create_all',
        # but would have failed in production.
        if os.environ.get("PATTY_TESTS_SKIP_MIGRATIONS", "false") == "true":
            with cls.engine.connect() as conn:
                conn.execute(create_exercise_number_collation)
                conn.commit()
            OrmBase.metadata.create_all(cls.engine)
        else:
            # This way of doing it is hacky (chdir, write to settings...), but is worth it as explained above.
            previous_dir = os.getcwd()
            previous_database_url = settings.DATABASE_URL
            try:
                os.chdir(os.path.dirname(__file__))
                settings.DATABASE_URL = cls.__database_url
                alembic.command.upgrade(alembic.config.Config(file_="alembic.ini"), "head")
            finally:
                settings.DATABASE_URL = previous_database_url
                os.chdir(previous_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        import sqlalchemy_utils.functions

        cls.engine.dispose()
        sqlalchemy_utils.functions.drop_database(cls.__database_url)
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.session = make_session(self.engine)

    def tearDown(self) -> None:
        self.session.close()
        super().tearDown()

    def add_model(self, __model: type[Model], **kwargs: Any) -> Model:
        instance = __model(**kwargs)
        self.session.add(instance)
        return instance

    def flush_model(self, __model: type[Model], **kwargs: Any) -> Model:
        instance = self.add_model(__model, **kwargs)
        self.session.flush()
        return instance

    def commit_model(self, __model: type[Model], **kwargs: Any) -> Model:
        instance = self.add_model(__model, **kwargs)
        self.session.commit()
        return instance

    def get_model(self, model: type[Model], pk: Any) -> Model:
        instance = self.session.get(model, pk)
        assert instance is not None
        return instance

    @contextlib.contextmanager
    def assert_integrity_error(self, name: str) -> typing.Generator[None, None, None]:
        with self.assertRaises(sqlalchemy.exc.IntegrityError) as cm:
            yield None
        assert isinstance(cm.exception.orig, psycopg2.errors.IntegrityError)
        self.assertEqual(cm.exception.orig.diag.constraint_name, name)
        self.session.rollback()
