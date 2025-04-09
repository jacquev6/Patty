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
    exercise_type = adapted.make_exercise_type(
        adapted.InstructionComponents(text=True, whitespace=True, choice=True),
        adapted.StatementComponents(
            text=True,
            whitespace=True,
            arrow=True,
            free_text_input=True,
            multiple_choices_input=True,
            selectable_input=True,
        ),
        adapted.ReferenceComponents(text=True, whitespace=True),
    )
    print(json.dumps(llm.make_schema(exercise_type), indent=2))


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
