from typing import Iterable
import ast
import asyncio
import colorsys
import datetime
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import textwrap
import time
import traceback
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

    print(json.dumps(app.openapi(), indent=2, sort_keys=True))


@main.command()
@click.argument("kind", type=click.Choice(["full", "modules"]))
def db_tables_graph(kind: typing.Literal["full", "modules"]) -> None:
    import graphviz  # type: ignore[import-untyped]
    import sqlalchemy as sql

    from . import database_utils
    from . import errors  # noqa: F401 to populate the metadata
    from . import external_exercises  # noqa: F401
    from . import sandbox  # noqa: F401
    from . import textbooks  # noqa: F401

    colors_by_annotation: dict[frozenset[str], str | None] = {
        frozenset({"adaptation"}): "#FF0000",
        frozenset({"adaptation", "sandbox"}): "#FF8888",
        frozenset({"classification"}): "#008800",
        frozenset({"classification", "sandbox"}): "#60AD60",
        frozenset({"errors"}): "#000000",
        frozenset({"exercises"}): "#000000",
        frozenset({"external"}): "#FF55FF",
        frozenset({"extraction"}): "#0000FF",
        frozenset({"extraction", "sandbox"}): "#5555FF",
        frozenset({"textbooks"}): "#FFFF00",
    }

    tables = database_utils.OrmBase.metadata.sorted_tables
    table_annotations = database_utils.table_annotations

    for table in tables:
        assert table_annotations[table.name] in colors_by_annotation

    tables_by_name: dict[str, sql.Table] = {table.name: table for table in tables}

    table_names_by_annotation: dict[frozenset[str], list[str]] = {
        annotation: sorted(table.name for table in tables if frozenset(table_annotations[table.name]) == annotation)
        for annotation in colors_by_annotation.keys()
    }

    graph = graphviz.Digraph(node_attr={"shape": "none"})
    graph.attr(rankdir="BT")

    if kind == "full":
        for annotation, node_color in colors_by_annotation.items():
            if node_color is not None:
                for table_name in table_names_by_annotation[annotation]:
                    table = tables_by_name[table_name]
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
                            filter(
                                lambda s: s != "", [pk_status, null_status] + foreign_keys_by_field.get(column.name, [])
                            )
                        )
                        fields.append(
                            f"""<TR><TD BGCOLOR="{color}">{column.name}</TD><TD BGCOLOR="{color}">{type}</TD><TD BGCOLOR="{color}">{status}</TD></TR>"""
                        )
                    graph.node(
                        table.name,
                        label=f"""<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD COLSPAN="3" BGCOLOR="#DDDDDD">{table.name}</TD></TR>{''.join(fields)}</TABLE>>""",
                        color=node_color,
                    )

                    for foreign_key_index, foreign_key in enumerate(foreign_keys):
                        target_table = foreign_key.elements[0].column.table.name
                        if target_table in tables_by_name:
                            label = f"FK{foreign_key_index+1} → " + ", ".join(
                                el.column.name for el in foreign_key.elements
                            )
                            graph.edge(table.name, target_table, label=label)

    elif kind == "modules":
        interesting_tables: set[str] = set()

        for table in tables:
            for foreign_key in table.foreign_key_constraints:
                target_table = foreign_key.elements[0].column.table.name
                if table_annotations[target_table] != table_annotations[table.name]:
                    interesting_tables.add(table.name)
                    interesting_tables.add(target_table)

        for annotation, node_color in colors_by_annotation.items():
            if node_color is not None:
                cluster = graphviz.Digraph(name=f"cluster_{'_'.join(annotation)}", node_attr={"shape": "box"})
                cluster.attr(label=" ".join(sorted(annotation)), color=node_color)

                for table_name in table_names_by_annotation[annotation]:
                    if table_name in interesting_tables:
                        cluster.node(table_name)

                graph.subgraph(cluster)

        for table in tables:
            for foreign_key in table.foreign_key_constraints:
                target_table = foreign_key.elements[0].column.table.name
                if table_annotations[target_table] != table_annotations[table.name]:
                    graph.edge(table.name, target_table)

    sys.stdout.buffer.write(graph.pipe(format="png"))


@main.command()
def python_dependency_graph() -> None:
    import graphviz

    ignored_packages = {
        # Imported many times, clutter the graph
        ("patty", "any_json"),
        ("patty", "api_utils"),
        ("patty", "database_utils"),
        ("patty", "settings"),
        ("patty", "version"),
        # Little interest, decrease readability
        ("patty", "migrations", "versions"),
    }

    def make_module_path(file_name: str) -> tuple[str, ...]:
        assert file_name.endswith(".py")
        return tuple(file_name[:-3].split(os.path.sep))

    def gather_dependencies(
        file_name: str, current_module_path: tuple[str, ...], known_module_paths: set[tuple[str, ...]]
    ) -> list[tuple[tuple[str, ...], bool]]:
        with open(file_name, "r") as file:
            content = file.read()
        module = ast.parse(content, filename=file_name)

        strong_dependencies: set[tuple[str, ...]] = set()
        weak_dependencies: set[tuple[str, ...]] = set()

        for nodes, dependencies in ((module.body, strong_dependencies), (ast.walk(module), weak_dependencies)):
            for node in nodes:
                if isinstance(node, ast.ImportFrom):
                    if node.level == 0:
                        # Absolute import
                        assert node.module is not None
                        imported_from = tuple(node.module.split("."))
                    else:
                        # Relative import
                        if node.module is None:
                            imported_from = current_module_path[: -node.level]
                        else:
                            imported_from = current_module_path[: -node.level] + tuple(node.module.split("."))

                    if imported_from[0] == "patty":
                        for name in node.names:
                            candidate: tuple[str, ...]
                            for candidate in ((name.name,), (name.name, "__init__"), ("__init__",), ()):
                                if imported_from + candidate in known_module_paths:
                                    dependencies.add(imported_from + candidate)
                                    break
                            else:
                                print("WARNING: unhandled import:", ast.unparse(node), file=sys.stderr)

                elif isinstance(node, ast.Import):
                    for name in node.names:
                        imported_what = tuple(name.name.split("."))
                        if imported_what[0] == "patty":
                            for candidate in (imported_what, imported_what + ("__init__",)):
                                if candidate in known_module_paths:
                                    dependencies.add(candidate)
                                    break
                            else:
                                print("WARNING: unhandled import:", ast.unparse(node), file=sys.stderr)

        ret = {}
        for dep in weak_dependencies:
            ret[dep] = current_module_path == ("patty", "__main__")
        for dep in strong_dependencies:
            ret[dep] = True

        return list(ret.items())

    def make_graph_node(module_path: tuple[str, ...]) -> str:
        return "_".join(module_path)

    def string_to_color(s: str) -> str:
        r, g, b = colorsys.hls_to_rgb(
            h=(int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16) % 360) / 360.0, l=0.5, s=1.0
        )
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def ignored(module_path: tuple[str, ...]) -> bool:
        return any(module_path[: len(ignored_package)] == ignored_package for ignored_package in ignored_packages)

    file_names = glob.glob("patty/**/*.py", recursive=True)
    known_module_paths = {make_module_path(file_name) for file_name in file_names}

    modules_dependency_graph = {
        module_path: set(
            (d, strong)
            for (d, strong) in gather_dependencies(file_name, module_path, known_module_paths)
            if not ignored(d)
        )
        for file_name in file_names
        for module_path in [make_module_path(file_name)]
        if not ignored(module_path)
    }

    clusters_by_package = {
        module_path[:-1]: graphviz.Digraph(
            name=f"cluster_{'_'.join(module_path[:-1])}",
            graph_attr={"label": module_path[-2], "color": string_to_color(".".join((*module_path[:-1], "__init__")))},
        )
        for module_path in modules_dependency_graph
    }

    for module_path in modules_dependency_graph.keys():
        clusters_by_package[module_path[:-1]].node(
            make_graph_node(module_path), label=module_path[-1], color=string_to_color(".".join(module_path))
        )

    for module_path, cluster in reversed(clusters_by_package.items()):
        if len(module_path) == 1:
            assert module_path[0] == "patty"
        else:
            clusters_by_package[module_path[:-1]].subgraph(cluster)

    graph = graphviz.Digraph(
        node_attr={"shape": "box"}, graph_attr={"rankdir": "BT", "compound": "true", "nodesep": "0.5", "ranksep": "1"}
    )
    graph.subgraph(clusters_by_package[("patty",)])

    for module_path, dependencies in modules_dependency_graph.items():
        for dependency, strong in dependencies:
            attrs = {"color": string_to_color(".".join(dependency)), "penwidth": "10"}
            if strong:
                attrs["weight"] = "10"
            else:
                attrs["weight"] = "1"
                attrs["style"] = "dashed"
            if dependency[-1] == "__init__":
                attrs["lhead"] = f"cluster_{'_'.join(dependency[:-1])}"
                attrs.pop("penwidth", None)
            if dependency[:-1] == module_path[: len(dependency) - 1]:
                attrs.pop("penwidth", None)
            graph.edge(make_graph_node(module_path), make_graph_node(dependency), **attrs)

    sys.stdout.buffer.write(graph.pipe(format="png"))


@main.command()
def tricky_sql_requests() -> None:
    import sqlparse  # type: ignore[import-untyped]

    from . import database_utils
    from . import extraction
    from . import textbooks

    database_engine = database_utils.create_engine(settings.DATABASE_URL)

    request: typing.Any
    for title, request in [
        ("Textbook.fetch_ordered_exercises", textbooks.Textbook.make_ordered_exercises_request(42)),
        (
            "PageExtraction.fetch_ordered_exercises (page and number)",
            extraction.PageExtraction.make_ordered_exercises_request__maybe_page_and_number(42),
        ),
        (
            "PageExtraction.fetch_ordered_exercises (textbook)",
            extraction.PageExtraction.make_ordered_exercises_request__textbook(42),
        ),
    ]:
        print(f"{title}:")
        print("=" * len(title))
        print(
            sqlparse.format(
                str(request.compile(database_engine, compile_kwargs={"literal_binds": True})),
                reindent=True,
                compact=False,
                keyword_case="upper",
                wrap_after=1,
            )
        )
        print()


@main.command()
@click.option("--choice/--no-choice", default=True, is_flag=True)
@click.option("--free-text-input/--no-free-text-input", default=True, is_flag=True)
@click.option("--multiple-choices-input/--no-multiple-choices-input", default=True, is_flag=True)
@click.option("--selectable-input/--no-selectable-input", default=True, is_flag=True)
@click.option("--swappable-input/--no-swappable-input", default=True, is_flag=True)
@click.option("--editable-text-input/--no-editable-text-input", default=True, is_flag=True)
@click.option("--split-word-input/--no-split-word-input", default=True, is_flag=True)
def adapted_exercise_schema(
    choice: bool,
    free_text_input: bool,
    multiple_choices_input: bool,
    selectable_input: bool,
    swappable_input: bool,
    editable_text_input: bool,
    split_word_input: bool,
) -> None:
    from . import adaptation

    exercise_type = adaptation.adapted.make_partial_exercise_type(
        adaptation.adapted.Components(
            instruction=adaptation.adapted.InstructionComponents(
                text=True, whitespace=True, arrow=True, formatted=True, image=True, choice=choice
            ),
            example=adaptation.adapted.ExampleComponents(
                text=True, whitespace=True, arrow=True, formatted=True, image=True
            ),
            hint=adaptation.adapted.HintComponents(text=True, whitespace=True, arrow=True, formatted=True, image=True),
            statement=adaptation.adapted.StatementComponents(
                text=True,
                whitespace=True,
                arrow=True,
                formatted=True,
                image=True,
                free_text_input=free_text_input,
                multiple_choices_input=multiple_choices_input,
                selectable_input=selectable_input,
                swappable_input=swappable_input,
                editable_text_input=editable_text_input,
                split_word_input=split_word_input,
            ),
            reference=adaptation.adapted.ReferenceComponents(
                text=True, whitespace=True, arrow=True, formatted=True, image=True
            ),
        )
    )
    schema = json.dumps(adaptation.llm.make_schema(exercise_type), indent=2)
    assert ('"choice"' in schema) == choice
    assert ('"freeTextInput"' in schema) == free_text_input
    assert ('"multipleChoicesInput"' in schema) == multiple_choices_input
    assert schema.count('"selectableInput"') == (2 if selectable_input else 1)
    assert ('"swappableInput"' in schema) == swappable_input
    assert ('"editableTextInput"' in schema) == editable_text_input
    print(schema)


@main.command()
def extracted_exercise_schema() -> None:
    from . import extraction

    print(json.dumps(extraction.extracted.ExercisesList.model_json_schema(), indent=2, ensure_ascii=False))


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

    from . import adaptation

    example_exercise = adaptation.adapted.ExerciseV1(
        format="v1",
        instruction=adaptation.adapted.InstructionPage(
            lines=[
                adaptation.adapted.InstructionLine(
                    contents=[
                        adaptation.adapted.Text(kind="text", text="Example"),
                        adaptation.adapted.Whitespace(kind="whitespace"),
                        adaptation.adapted.Text(kind="text", text="exercise"),
                        adaptation.adapted.Whitespace(kind="whitespace"),
                        adaptation.adapted.Text(kind="text", text="instruction"),
                        adaptation.adapted.Text(kind="text", text="."),
                    ]
                )
            ]
        ),
        example=None,
        hint=None,
        statement=adaptation.adapted.StatementPagesV1(
            pages=[
                adaptation.adapted.StatementPage(
                    lines=[
                        adaptation.adapted.StatementLine(
                            contents=[
                                adaptation.adapted.Text(kind="text", text="Example"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="exercise"),
                                adaptation.adapted.Whitespace(kind="whitespace"),
                                adaptation.adapted.Text(kind="text", text="statement"),
                                adaptation.adapted.Text(kind="text", text="."),
                            ]
                        )
                    ]
                )
            ]
        ),
        reference=None,
    )
    usage = subprocess.run(
        ["black", "--line-length", "80", "--skip-magic-trailing-comma", "-"],
        input=textwrap.dedent(
            f"""\
        from patty_json_to_html import exercise_to_html, textbook_to_html

        exercise = {example_exercise.model_dump()!r}

        print(exercise_to_html(exercise))

        textbook = {{
            "title": "Example Textbook",
            "exercises": [{{"page": 12, "number": "23", "exercise": exercise}}],
        }}

        print(textbook_to_html(textbook))
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
        yield "Example usage (note that `exercise_to_html` also accepts an instance of `Exercise`, and `textbook_to_html` an instance of `Textbook`):"
        yield ""
        continuation = False
        for line in usage.splitlines():
            line = line.rstrip()
            if line == "":
                yield ""
                continuation = False
            elif continuation:
                yield f"... {line}"
            else:
                yield f">>> {line}"
                continuation = True
            if line.startswith("print"):
                yield "<!doctype html>"
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
        yield "import pydantic.alias_generators"
        yield ""
        with open("patty/adaptation/adapted.py") as f:
            for line in f:
                if line.rstrip() == "# patty_json_to_html.py begin":
                    break
            for line in f:
                if line.rstrip() == "# patty_json_to_html.py end":
                    break
                if line.strip().startswith("# WARNING:"):
                    continue
                yield line.rstrip()
        yield ""
        yield "def exercise_to_html(exercise: ExerciseAsUnion | dict[str, Any]) -> str:"
        yield "    if not isinstance(exercise, ExerciseAsUnion):"
        yield "        exercise = Exercise.model_validate(exercise).root"
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
        yield ""
        yield "class TextbookExercise(pydantic.BaseModel):"
        yield "    page: int"
        yield "    number: str"
        yield "    exercise: Exercise"
        yield ""
        yield "class Textbook(pydantic.BaseModel):"
        yield "    title: str"
        yield "    exercises: list[TextbookExercise]"
        yield ""
        yield "def textbook_to_html(textbook: Textbook | dict[str, Any]) -> str:"
        yield "    if not isinstance(textbook, Textbook):"
        yield "        textbook = Textbook.model_validate(textbook)"
        yield ""
        with open("patty/export/templates/textbook/index.html") as f:
            yield f"    template = {f.read().strip()!r}"
        yield ""
        yield "    exercises = []"
        yield "    for exercise in textbook.exercises:"
        yield "        exercise_dump = exercise.exercise.model_dump()"
        yield "        exercises.append({"
        yield '            "exerciseId": f"P{exercise.page}Ex{exercise.number}",'
        yield '            "pageNumber": exercise.page,'
        yield '            "exerciseNumber": exercise.number,'
        yield '            "kind": "adapted",'
        yield '            "studentAnswersStorageKey": hashlib.md5(json.dumps(exercise_dump, separators=(",", ":"), indent=None).encode()).hexdigest(),'
        yield '            "adaptedExercise": exercise_dump,'
        yield "        })"
        yield '    data = {"title": textbook.title, "exercises": exercises}'
        yield ""
        yield "    return template.replace("
        yield '        "##TO_BE_SUBSTITUTED_TEXTBOOK_EXPORT_DATA##",'
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
    from . import adaptation
    from . import classification
    from . import extraction

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
                    go_on = (
                        len(
                            await asyncio.gather(
                                *extraction.submission.submit_extractions(session, extraction_parallelism)
                            )
                        )
                        == 0
                    )
                    if go_on:
                        go_on = not classification.submission.submit_classifications(
                            session, classification_parallelism
                        )
                        if go_on:
                            await asyncio.gather(
                                *adaptation.submission.submit_adaptations(session, adaptation_parallelism)
                            )
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
# @todo Consider always using the most recent backup (and stop changing the default value)
@click.argument("backup_url", default="s3://jacquev6/patty/prod/backups/patty-backup-20250923-131603.tar.gz")
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
@click.option("--dry-run", is_flag=True)
def migrate_data(dry_run: bool) -> None:
    from . import database_utils
    from . import data_migration

    database_engine = database_utils.create_engine(settings.DATABASE_URL)
    with database_utils.make_session(database_engine) as session:
        data_migration.migrate(session)
        session.flush()
        data_migration.validate(session)
        if not dry_run:
            session.commit()


if __name__ == "__main__":
    main()
