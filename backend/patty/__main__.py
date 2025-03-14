import io
import json

import click

from . import asgi
from . import tokenization


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
def tokenized_text_schema(output: io.StringIO) -> None:
    json.dump(tokenization.TokenizedText.model_json_schema(), output, indent=2)
    output.write("\n")


if __name__ == "__main__":
    main()
