import copy
import re
import sys
from typing import Iterable
from urllib.parse import urlparse
import datetime
import io
import json
import os
import subprocess
import tarfile

import sqlalchemy_utils

import boto3
import click
import requests

from . import adaptation
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
        ),
        adapted.ReferenceComponents(text=True, whitespace=True, arrow=True, formatted=True),
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


parsed_database_url = urlparse(settings.DATABASE_URL)
assert parsed_database_url.scheme == "postgresql+psycopg2"

parsed_database_backups_url = urlparse(settings.DATABASE_BACKUPS_URL)


@main.command()
def backup_database() -> None:
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
@click.argument("backup_url")
@click.option("--yes", is_flag=True)
@click.option("--patch-according-to-settings", is_flag=True)
def restore_database(backup_url: str, yes: bool, patch_according_to_settings: bool) -> None:
    parsed_backup_url = urlparse(backup_url)

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
    parsed_placeholder_database_url = urlparse(placeholder_database_url)
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
    database_engine = database_utils.create_engine(settings.DATABASE_URL)

    # Migrate JSON fields according to evolution of schemas
    with database_utils.make_session(database_engine) as session:
        for strategy in session.query(adaptation.Strategy).all():
            spec = copy.deepcopy(strategy._response_specification)
            if spec["format"] == "json" and spec["formalism"] == "json-schema":
                spec["instruction_components"].setdefault("arrow", True)
                spec["instruction_components"].setdefault("formatted", True)
                spec["example_components"].setdefault("formatted", True)
                spec["hint_components"].setdefault("arrow", True)
                spec["hint_components"].setdefault("formatted", True)
                spec["statement_components"].setdefault("swappable_input", False)
                spec["statement_components"].setdefault("formatted", True)
                spec["reference_components"].setdefault("arrow", True)
                spec["reference_components"].setdefault("formatted", True)
            strategy._response_specification = spec
        session.commit()

    # Check that all JSON fields are valid
    with database_utils.make_session(database_engine) as session:
        for adaptation_ in session.query(adaptation.Adaptation).all():
            # No need to check 'adaptation_.raw_llm_conversations': it has no schema
            adaptation_.initial_assistant_response
            adaptation_.adjustments
            adaptation_.manual_edit
        for batch in session.query(adaptation.Batch).all():
            pass
        for input in session.query(adaptation.Input).all():
            pass
        for strategy in session.query(adaptation.Strategy).all():
            strategy.model
            strategy.response_specification


if __name__ == "__main__":
    main()
