import io
import json

import click

from . import asgi


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("output", type=click.File("w"))
def openapi(output: io.StringIO) -> None:
    json.dump(asgi.app.openapi(), output, indent=2)
    output.write("\n")


assert __name__ == "__main__"
main()
