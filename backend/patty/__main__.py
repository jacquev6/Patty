from typing import Iterable
import io
import json

import click

from . import adaptation
from . import asgi
from . import database_utils
from . import fixtures
from . import settings


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("output", type=click.File("w"))
def openapi(output: io.StringIO) -> None:
    json.dump(asgi.app.openapi(), output, indent=2)
    output.write("\n")


@main.command()
@click.argument("output", type=click.File("w"))
def adapted_exercise_schema(output: io.StringIO) -> None:
    json.dump(adaptation.AdaptedExercise.model_json_schema(), output, indent=2)
    output.write("\n")


@main.command()
@click.argument("fixture", type=str, nargs=-1)
def load_fixtures(fixture: Iterable[str]) -> None:
    database_engine = database_utils.create_engine(settings.DATABASE_URL)
    with database_utils.make_session(database_engine) as session:
        fixtures.load(session, fixture)
        session.commit()


if __name__ == "__main__":
    main()
