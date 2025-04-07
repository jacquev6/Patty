from typing import Iterable
import json

import click

from . import adapted
from . import asgi
from . import database_utils
from . import fixtures
from . import llm
from . import settings


@click.group()
def main() -> None:
    pass


@main.command()
def openapi() -> None:
    print(json.dumps(asgi.app.openapi(), indent=2))


@main.command()
def adapted_exercise_schema() -> None:
    print(json.dumps(llm.make_schema(adapted.Exercise), indent=2))


@main.command()
def default_system_prompt() -> None:
    print(fixtures.make_default_system_prompt())


@main.command()
@click.argument("fixture", type=str, nargs=-1)
def load_fixtures(fixture: Iterable[str]) -> None:
    database_engine = database_utils.create_engine(settings.DATABASE_URL)
    with database_utils.make_session(database_engine) as session:
        fixtures.load(session, fixture)
        session.commit()


if __name__ == "__main__":
    main()
