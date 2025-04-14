from typing import Annotated, Iterable, cast

from fastapi import Depends, Request
import sqlalchemy.orm
import sqlalchemy.exc


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


class SessionMaker:
    def __init__(self, engine: Engine) -> None:
        self.__engine = engine

    def __call__(self) -> Session:
        return make_session(self.__engine)


def _session_dependable(request: Request) -> Iterable[Session]:
    with cast(SessionMaker, request.app.extra["make_session"])() as session:
        try:
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()


SessionDependable = Annotated[Session, Depends(_session_dependable)]
