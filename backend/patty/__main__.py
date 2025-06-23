import textwrap
import time
import traceback
from typing import Iterable
import asyncio
import datetime
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import typing
import urllib.parse

# In this file, we favor importing third-party and local modules in the appropriate command functions to avoid
# loading unused modules. Before doing that, 'python -m patty --help' took 6s. Now it takes less than 1s.

import click

from . import settings


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("password")
def hash_password(password: str) -> None:
    import argon2

    print(argon2.PasswordHasher().hash(password))


@main.command()
def openapi() -> None:
    import fastapi

    from . import asgi

    app = fastapi.FastAPI()
    app.include_router(asgi.openapi_router)

    print(json.dumps(app.openapi(), indent=2))


@main.command()
def db_tables_graph() -> None:
    import graphviz  # type: ignore[import-untyped]
    import sqlalchemy

    from . import orm_models

    models = orm_models.all_models
    tables = [typing.cast(sqlalchemy.Table, model.__table__) for model in models]
    known_table_names = set(table.name for table in tables)

    graph = graphviz.Digraph(node_attr={"shape": "none"})
    for table in tables:
        foreign_keys = sorted(table.foreign_key_constraints, key=lambda fk: typing.cast(str, fk.name))

        foreign_keys_by_field: dict[str, list[str]] = {}
        for foreign_key_index, foreign_key in enumerate(foreign_keys):
            for column in foreign_key.columns:
                foreign_keys_by_field.setdefault(column.name, []).append(f"FK{foreign_key_index+1}")

        fields = []
        for column_index, column in enumerate(table.columns):
            color = ["#AAAAAA", "#DDDDDD"][column_index % 2]
            type = str(column.type)
            if " " in type:
                type = "<BR/>".join(type.split(" ", 1))
            pk_status = "PK" if column.primary_key else ""
            null_status = "nullable" if column.nullable else ""
            status = ", ".join(
                filter(lambda s: s != "", [pk_status, null_status] + foreign_keys_by_field.get(column.name, []))
            )
            fields.append(
                f"""<TR><TD BGCOLOR="{color}">{column.name}</TD><TD BGCOLOR="{color}">{type}</TD><TD BGCOLOR="{color}">{status}</TD></TR>"""
            )
        graph.node(
            table.name,
            label=f"""<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD COLSPAN="3" BGCOLOR="#DDDDDD">{table.name}</TD></TR>{''.join(fields)}</TABLE>>""",
        )

        for foreign_key_index, foreign_key in enumerate(foreign_keys):
            target_table = foreign_key.elements[0].column.table.name
            if target_table in known_table_names:
                label = f"FK{foreign_key_index+1} → " + ", ".join(el.column.name for el in foreign_key.elements)
                graph.edge(table.name, target_table, label=label)

    sys.stdout.buffer.write(graph.pipe(format="png"))


@main.command()
def adapted_exercise_schema() -> None:
    from . import adapted
    from .adaptation import llm

    exercise_type = adapted.make_exercise_type(
        adapted.InstructionComponents(text=True, whitespace=True, arrow=True, formatted=True, choice=True),
        adapted.ExampleComponents(text=True, whitespace=True, arrow=True, formatted=True),
        adapted.HintComponents(text=True, whitespace=True, arrow=True, formatted=True),
        adapted.StatementComponents(
            text=True,
            whitespace=True,
            arrow=True,
            formatted=True,
            free_text_input=True,
            multiple_choices_input=True,
            selectable_input=True,
            swappable_input=True,
            editable_text_input=True,
        ),
        adapted.ReferenceComponents(text=True, whitespace=True, arrow=True, formatted=True),
    )
    print(json.dumps(llm.make_schema(exercise_type), indent=2))


@main.command()
def extracted_exercise_schema() -> None:
    from . import extracted

    print(json.dumps(extracted.ExercisesList.model_json_schema(), indent=2, ensure_ascii=False))


@main.command()
def default_adaptation_prompt() -> None:
    from . import fixtures

    print(fixtures.make_default_adaptation_prompt())


@main.command()
def default_extraction_prompt() -> None:
    from . import fixtures

    print(fixtures.make_default_extraction_prompt())


@main.command()
def json_to_html_script() -> None:
    # This is pretty hacky, but it avoids the complexity of versioning and packaging Patty,
    # and allows @eliselinc to download a single file and add it to her source tree.

    from . import adapted

    example_exercise = adapted.Exercise(
        format="v1",
        instruction=adapted.InstructionPage(
            lines=[
                adapted.InstructionLine(
                    contents=[
                        adapted.Text(kind="text", text="Example"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Text(kind="text", text="exercise"),
                        adapted.Whitespace(kind="whitespace"),
                        adapted.Text(kind="text", text="instruction"),
                        adapted.Text(kind="text", text="."),
                    ]
                )
            ]
        ),
        example=None,
        hint=None,
        statement=adapted.StatementPages(
            pages=[
                adapted.StatementPage(
                    lines=[
                        adapted.StatementLine(
                            contents=[
                                adapted.Text(kind="text", text="Example"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="exercise"),
                                adapted.Whitespace(kind="whitespace"),
                                adapted.Text(kind="text", text="statement"),
                                adapted.Text(kind="text", text="."),
                            ]
                        )
                    ]
                )
            ]
        ),
        reference=None,
    )
    usage = subprocess.run(
        ["black", "--line-length", "116", "--skip-magic-trailing-comma", "-"],
        input=textwrap.dedent(
            f"""\
        from patty_json_to_html import json_to_html

        exercise = {example_exercise.model_dump()!r}

        print(json_to_html(exercise))
        """
        ),
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    def gen() -> typing.Iterable[str]:
        yield "# This file is *generated* by Patty. Do not edit it directly."
        yield ""
        yield '"""'
        yield "Example usage (note that `json_to_html` also accepts an instance of `Exercise`):"
        yield ""
        for line in usage.splitlines():
            line = line.rstrip()
            if line == "":
                yield ""
            elif any(line.startswith(prefix) for prefix in ("from", "exercise", "print")):
                yield f">>> {line}"
            else:
                yield f"... {line}"
        yield "<!DOCTYPE html>"
        yield '<html lang="">'
        yield "  ..."
        yield "</html>"
        yield '"""'
        yield ""
        yield ""
        yield "from __future__ import annotations"
        yield "from typing import Any, Literal"
        yield "import hashlib"
        yield "import json"
        yield ""
        yield "import pydantic"
        yield ""
        with open("patty/adapted.py") as f:
            for line in f:
                if line.rstrip() == "# patty_json_to_html.py begin":
                    break
            for line in f:
                if line.rstrip() == "# patty_json_to_html.py end":
                    break
                if line.strip().startswith("# WARNING:"):
                    continue
                yield line.rstrip()
        yield "def json_to_html(exercise: Exercise | dict[str, Any]) -> str:"
        yield "    if not isinstance(exercise, Exercise):"
        yield "        exercise = Exercise.model_validate(exercise)"
        yield ""
        with open("patty/export/templates/adaptation/index.html") as f:
            yield f"    template = {f.read().strip()!r}"
        yield ""
        yield "    exercise_dump = exercise.model_dump()"
        yield "    data = {"
        yield '        "studentAnswersStorageKey": hashlib.md5(json.dumps(exercise_dump, separators=(",", ":"), indent=None).encode()).hexdigest(),'
        yield '        "adaptedExercise": exercise_dump,'
        yield "    }"
        yield ""
        yield "    return template.replace("
        yield '        "##TO_BE_SUBSTITUTED_ADAPTATION_EXPORT_DATA##",'
        yield "        json.dumps(data).replace('\\\\', '\\\\\\\\').replace('\\\"', '\\\\\"'),"
        yield "    )"

    subprocess.run(
        ["black", "--line-length", "120", "--skip-magic-trailing-comma", "-"],
        input="\n".join(gen()),
        text=True,
        check=True,
    )


@main.command()
@click.option("--truncate", is_flag=True, help="Truncate DB before loading")
@click.argument("fixture", type=str, nargs=-1)
def load_fixtures(truncate: bool, fixture: Iterable[str]) -> None:
    from . import database_utils
    from . import fixtures

    database_engine = database_utils.create_engine(settings.DATABASE_URL)
    with database_utils.make_session(database_engine) as session:
        fixtures.load(session, truncate, fixture)
        session.commit()


@main.command()
@click.option("--extraction-parallelism", type=int, default=1)
@click.option("--classification-parallelism", type=int, default=20)
@click.option("--adaptation-parallelism", type=int, default=1)
@click.option("--pause", type=float, default=1.0)
def run_submission_daemon(
    extraction_parallelism: int, classification_parallelism: int, adaptation_parallelism: int, pause: float
) -> None:
    import requests

    from . import database_utils
    from .adaptation.submission import submit_adaptations
    from .classification import submit_classifications
    from .extraction.submission import submit_extractions

    def log(message: str) -> None:
        # @todo Use actual logging
        print(datetime.datetime.now(), message, flush=True)

    engine = database_utils.create_engine(settings.DATABASE_URL)

    async def daemon() -> None:
        log("Starting")
        last_time = time.monotonic()
        while True:
            try:
                with database_utils.Session(engine) as session:
                    # Do only one thing (extract OR classify OR adapt): it's easier to understand logs that way
                    go_on = len(await asyncio.gather(*submit_extractions(session, extraction_parallelism))) == 0
                    if go_on:
                        go_on = not submit_classifications(session, classification_parallelism)
                        if go_on:
                            await asyncio.gather(*submit_adaptations(session, adaptation_parallelism))
                    session.commit()
                if time.monotonic() >= last_time + 60:
                    log("Calling pulse monitoring URL")
                    last_time = time.monotonic()
                    requests.post(settings.SUBMISSION_DAEMON_PULSE_MONITORING_URL)
            except Exception:  # Pokemon programming: gotta catch 'em all
                log("UNEXPECTED ERROR reached daemon level")
                traceback.print_exc()
            log(f"Sleeping for {pause}s...")
            await asyncio.sleep(pause)

    asyncio.run(daemon())


parsed_database_url = urllib.parse.urlparse(settings.DATABASE_URL)
assert parsed_database_url.scheme == "postgresql+psycopg2"

parsed_database_backups_url = urllib.parse.urlparse(settings.DATABASE_BACKUPS_URL)


@main.command()
def backup_database() -> None:
    import boto3
    import requests

    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"patty-backup-{now}"
    archive_name = f"{backup_name}.tar.gz"

    print(
        f"Backing up database {settings.DATABASE_URL} to {settings.DATABASE_BACKUPS_URL}/{archive_name}",
        file=sys.stderr,
    )

    assert parsed_database_url.hostname is not None
    assert parsed_database_url.username is not None
    assert parsed_database_url.password is not None

    pg_dump = subprocess.run(
        [
            # fmt: off
            "pg_dump",
            "--host", parsed_database_url.hostname,
            "--username", parsed_database_url.username,
            "--no-password",
            "--dbname", parsed_database_url.path[1:],
            "--file", "-",
            "--create", "--column-inserts", "--quote-all-identifiers",
            # fmt: on
        ],
        env=dict(os.environ, PGPASSWORD=parsed_database_url.password),
        check=True,
        capture_output=True,
    )

    def populate_tarball(tarball: tarfile.TarFile) -> None:
        info = tarfile.TarInfo(f"{backup_name}/pg_dump.sql")
        info.size = len(pg_dump.stdout)
        tarball.addfile(info, io.BytesIO(pg_dump.stdout))

    if parsed_database_backups_url.scheme == "file":
        with tarfile.open(os.path.join(parsed_database_backups_url.path, archive_name), "w:gz") as tarball:
            populate_tarball(tarball)
    elif parsed_database_backups_url.scheme == "s3":
        assert "AWS_ACCESS_KEY_ID" in os.environ
        assert "AWS_SECRET_ACCESS_KEY" in os.environ
        s3 = boto3.client("s3")
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tarball:
            populate_tarball(tarball)
        buffer.seek(0)
        s3.upload_fileobj(
            buffer, parsed_database_backups_url.netloc, f"{parsed_database_backups_url.path[1:]}/{archive_name}"
        )
    else:
        raise NotImplementedError(f"Unsupported database backup URL scheme: {parsed_database_backups_url.scheme}")

    requests.post(
        settings.DATABASE_BACKUP_PULSE_MONITORING_URL,
        json={"archive_url": f"{settings.DATABASE_BACKUPS_URL}/{archive_name}"},
    )
    print(
        f"Backed up database {settings.DATABASE_URL} to {settings.DATABASE_BACKUPS_URL}/{archive_name}", file=sys.stderr
    )


@main.command()
@click.argument("backup_url", default="s3://jacquev6/patty/prod/backups/patty-backup-20250619-041608.tar.gz")
@click.option("--yes", is_flag=True)
@click.option("--patch-according-to-settings", is_flag=True)
def restore_database(backup_url: str, yes: bool, patch_according_to_settings: bool) -> None:
    import boto3
    import sqlalchemy_utils

    parsed_backup_url = urllib.parse.urlparse(backup_url)

    if parsed_backup_url.scheme == "file":
        with tarfile.open(parsed_backup_url.path, "r:gz") as tarball:
            pg_dump_file = tarball.extractfile(tarball.getnames()[0])
            assert pg_dump_file is not None
            pg_dump = pg_dump_file.read()
    elif parsed_backup_url.scheme == "s3":
        assert "AWS_ACCESS_KEY_ID" in os.environ
        assert "AWS_SECRET_ACCESS_KEY" in os.environ
        s3 = boto3.client("s3")
        buffer = io.BytesIO()
        s3.download_fileobj(parsed_backup_url.netloc, f"{parsed_backup_url.path[1:]}", buffer)
        buffer.seek(0)
        with tarfile.open(fileobj=buffer, mode="r:gz") as tarball:
            pg_dump_file = tarball.extractfile(tarball.getnames()[0])
            assert pg_dump_file is not None
            pg_dump = pg_dump_file.read()
    else:
        raise NotImplementedError(f"Unsupported database backup URL scheme: {parsed_database_backups_url.scheme}")

    print(f"Restoring database {settings.DATABASE_URL} from {backup_url} ({len(pg_dump)} bytes)", file=sys.stderr)
    if not yes:
        print(
            "This will overwrite the current database. Are you sure you want to continue? [y/N]",
            file=sys.stderr,
            end=" ",
        )
        if input().strip().lower() != "y":
            print("Aborting.", file=sys.stderr)
            return

    placeholder_database_url = settings.DATABASE_URL + "-restore"
    if not sqlalchemy_utils.functions.database_exists(placeholder_database_url):
        sqlalchemy_utils.functions.create_database(placeholder_database_url)
    parsed_placeholder_database_url = urllib.parse.urlparse(placeholder_database_url)
    assert parsed_placeholder_database_url.hostname is not None
    assert parsed_placeholder_database_url.username is not None
    assert parsed_placeholder_database_url.password is not None

    if sqlalchemy_utils.functions.database_exists(settings.DATABASE_URL):
        sqlalchemy_utils.functions.drop_database(settings.DATABASE_URL)

    sql = pg_dump.decode()
    if patch_according_to_settings:
        # Comments
        sql = re.sub(r" Owner: \w+", f" Owner: {parsed_database_url.username}", sql)
        sql = re.sub(r"-- Name: \w+; Type: DATABASE;", f"-- Name: {parsed_database_url.path[1:]}; Type: DATABASE;", sql)
        # Postgres commands
        sql = re.sub(r"connect \"\w+\"", f'connect "{parsed_database_url.path[1:]}"', sql)
        # Actual SQL
        sql = re.sub(r" OWNER TO \"\w+\";", f' OWNER TO "{parsed_database_url.username}";', sql)
        sql = re.sub(r"DATABASE \"\w+\"", f'DATABASE "{parsed_database_url.path[1:]}"', sql)

    subprocess.run(
        [
            # fmt: off
            "psql",
            "--host", parsed_placeholder_database_url.hostname,
            "--username", parsed_placeholder_database_url.username,
            "--no-password",
            "--dbname", parsed_placeholder_database_url.path[1:],
            # fmt: on
        ],
        env=dict(os.environ, PGPASSWORD=parsed_placeholder_database_url.password),
        check=True,
        input=sql,
        universal_newlines=True,
    )

    sqlalchemy_utils.functions.drop_database(placeholder_database_url)


@main.command()
def migrate_data() -> None:
    from . import database_utils
    from . import data_migration

    database_engine = database_utils.create_engine(settings.DATABASE_URL)
    with database_utils.make_session(database_engine) as session:
        data_migration.migrate(session)
        session.commit()


if __name__ == "__main__":
    main()
