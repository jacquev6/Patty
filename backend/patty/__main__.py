import io
import json

import click

from . import adaptation
from . import asgi


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


if __name__ == "__main__":
    main()
