# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import glob
import os
import shutil
import subprocess

import click

from .cycle import DevelopmentCycle, DevelopmentCycleError
from . import compose
from ..main_command import main


@main.group()
def dev() -> None:
    pass


@dev.command()
@click.option("--force", is_flag=True)
def clean(force: bool) -> None:
    lines = subprocess.run(["git", "clean", "-nXd"], capture_output=True, universal_newlines=True).stdout.splitlines()
    assert all(line.startswith("Would remove ") for line in lines)
    candidates = [line[13:] for line in lines]

    for candidate in candidates:
        remove = False
        if any(
            candidate.startswith(prefix)
            for prefix in [
                ".mypy_cache/",
                ".ruff_cache/",
                "backend/",
                "frontend/",
                "support/dev-env/backend/annotated-pdf-pages/",
                "support/dev-env/backend/exercise-images/",
                "support/dev-env/backend/external-exercises/",
                "support/dev-env/backend/home-config/",
                "support/dev-env/backend/home-local/",
                "support/dev-env/backend/pdf-files/",
                "support/dev-env/db/backups/",
                "support/dev-env/db/dumps/",
                "support/dev-env/frontend/cache/",
                "support/prod/backend/exercise-images/",
                "support/prod/backend/external-exercises/",
                "support/prod/backend/pdf-files/",
                "support/prod/db/backups/",
            ]
        ):
            remove = True

        if remove:
            if force:
                print("Removing", candidate)
                if candidate.endswith("/"):
                    shutil.rmtree(candidate)
                else:
                    os.unlink(candidate)
            else:
                print("Would remove", candidate)
        else:
            print("Keeping", candidate)


@dev.command()
@click.option("--build/--no-build", is_flag=True, default=True)
@click.option("--keep-up-on-error", is_flag=True, default=False)
def run(build: bool, keep_up_on_error: bool) -> None:
    """Run the development environment. Stop it with Ctrl+C."""

    if build:
        print("Patty dev env: build")
        subprocess.run(["docker", "compose", "build"], cwd="support/dev-env", check=True)
        print("Patty dev env: pull")
        subprocess.run(["docker", "compose", "pull", "--ignore-buildable"], cwd="support/dev-env", check=True)

    print("Patty dev env: start")
    try:
        subprocess.run(
            ["docker", "compose", "up", "--no-build", "--pull", "never", "--remove-orphans", "--detach"],
            cwd="support/dev-env",
            check=True,
        )
        print("Patty dev env: started (close with Ctrl+C)")
        try:
            subprocess.run(["docker", "compose", "logs", "--follow"], cwd="support/dev-env", check=False)
        except KeyboardInterrupt:
            pass
    finally:
        if not keep_up_on_error:
            print("Patty dev env: clean-up")
            subprocess.run(["docker", "compose", "down", "--remove-orphans"], cwd="support/dev-env", check=True)
            subprocess.run(
                ["docker", "compose", "rm", "--stop", "--volumes", "--force"], cwd="support/dev-env", check=True
            )


@dev.command(name="compose")
@click.argument("args", nargs=-1)
def compose_(args: tuple[str, ...]) -> None:
    subprocess.run(["docker", "compose"] + list(args), cwd="support/dev-env", check=True)


@dev.command()
@click.argument("args", nargs=-1)
def patty(args: tuple[str, ...]) -> None:
    compose.exec_in_backend_container(["python", "-m", "patty"] + list(args), check=True)


@dev.command()
@click.argument("args", nargs=-1)
def alembic(args: tuple[str, ...]) -> None:
    compose.exec_in_backend_container(["alembic"] + list(args), workdir="/app/backend/patty", check=True)


@dev.command()
@click.option("--cost-money", is_flag=True)
@click.option("--only-backend", is_flag=True)
@click.option("--skip-backend", is_flag=True)
@click.option("--only-frontend", is_flag=True)
@click.option("--skip-frontend", is_flag=True)
@click.option("--only-e2e", is_flag=True)
@click.option("--skip-e2e", is_flag=True)
@click.option("--allow-outdated-database", is_flag=True)
@click.option("--only-migration", is_flag=True)
@click.option("--skip-migration", is_flag=True)
@click.option("--skip-schema-revision", is_flag=True)
@click.option("--only-format", is_flag=True)
@click.option("--skip-format", is_flag=True)
@click.option("--only-lint", is_flag=True)
@click.option("--skip-lint", is_flag=True)
@click.option("--only-type-check", is_flag=True)
@click.option("--skip-type-check", is_flag=True)
@click.option("--only-test", is_flag=True)
@click.option("--skip-test", is_flag=True)
@click.option("--only-spec", type=str, multiple=True)
@click.option("--skip-spec", type=str, multiple=True)
@click.option("--only-electron", is_flag=True)
@click.option("--skip-electron", is_flag=True)
@click.option("--only-chromium", is_flag=True)
@click.option("--skip-chromium", is_flag=True)
@click.option("--only-firefox", is_flag=True)
@click.option("--skip-firefox", is_flag=True)
@click.option("--accept-visual-diffs", is_flag=True)
def cycle(
    cost_money: bool,
    only_backend: bool,
    skip_backend: bool,
    only_frontend: bool,
    skip_frontend: bool,
    only_e2e: bool,
    skip_e2e: bool,
    allow_outdated_database: bool,
    only_migration: bool,
    skip_migration: bool,
    skip_schema_revision: bool,
    only_format: bool,
    skip_format: bool,
    only_lint: bool,
    skip_lint: bool,
    only_type_check: bool,
    skip_type_check: bool,
    only_test: bool,
    skip_test: bool,
    only_spec: tuple[str, ...],
    skip_spec: tuple[str, ...],
    only_electron: bool,
    skip_electron: bool,
    only_chromium: bool,
    skip_chromium: bool,
    only_firefox: bool,
    skip_firefox: bool,
    accept_visual_diffs: bool,
) -> None:
    """Run the development cycle."""

    any_only = only_backend or only_frontend or only_e2e
    do_backend = not skip_backend and not any_only
    do_frontend = not skip_frontend and not any_only
    do_end_to_end = not skip_e2e and not any_only
    if only_backend:
        do_backend = True
    if only_frontend:
        do_frontend = True
    if only_e2e:
        do_end_to_end = True

    any_only = only_migration or only_format or only_lint or only_type_check or only_test
    do_migration = not skip_migration and not any_only
    do_schema_revision = not skip_schema_revision
    do_format = not skip_format and not any_only
    do_lint = not skip_lint and not any_only
    do_type_check = not skip_type_check and not any_only
    do_test = not skip_test and not any_only
    if only_migration:
        do_migration = True
    if only_format:
        do_format = True
    if only_lint:
        do_lint = True
    if only_type_check:
        do_type_check = True
    if only_test:
        do_test = True

    any_only = only_electron or only_chromium or only_firefox
    do_electron = not skip_electron and not any_only
    do_chromium = not skip_chromium and not any_only
    do_firefox = not skip_firefox and not any_only
    if only_electron:
        do_electron = True
    if only_chromium:
        do_chromium = True
    if only_firefox:
        do_firefox = True
    browsers = []
    if do_electron:
        browsers.append("electron")
    if do_chromium:
        browsers.append("chromium")
    if do_firefox:
        browsers.append("firefox")

    all_frontend_specs = set(filter(os.path.isfile, glob.glob("frontend/src/**/*.cy.ts", recursive=True)))
    only_frontend_specs = set(only_spec) & all_frontend_specs
    skip_frontend_specs = set(skip_spec) & all_frontend_specs
    if only_frontend_specs:
        frontend_specs = sorted(only_frontend_specs)
    else:
        frontend_specs = sorted(all_frontend_specs - skip_frontend_specs)

    all_e2e_specs = set(filter(os.path.isfile, glob.glob("frontend/e2e-tests/**/*.cy.ts", recursive=True)))
    only_e2e_specs = set(only_spec) & all_e2e_specs
    skip_e2e_specs = set(skip_spec) & all_e2e_specs
    if only_e2e_specs:
        end_to_end_specs = sorted(only_e2e_specs)
    else:
        end_to_end_specs = sorted(all_e2e_specs - skip_e2e_specs)

    unknown_specs = (set(only_spec) | set(skip_spec)) - (all_frontend_specs | all_e2e_specs)
    for spec in unknown_specs:
        raise ValueError(f"Invalid spec: {spec}")

    cycle = DevelopmentCycle(
        do_migration=do_migration,
        allow_outdated_database=allow_outdated_database,
        do_schema_revision=do_schema_revision,
        cost_money=cost_money,
        do_backend=do_backend,
        do_frontend=do_frontend,
        do_end_to_end=do_end_to_end,
        do_format=do_format,
        do_lint=do_lint,
        do_type_check=do_type_check,
        do_test=do_test,
        frontend_specs=frontend_specs,
        end_to_end_specs=end_to_end_specs,
        browsers=browsers,
        accept_visual_diffs=accept_visual_diffs,
    )
    try:
        cycle.run()
    except DevelopmentCycleError as e:
        print(f"Development cycle failed: {e}")
        raise click.Abort()


@dev.group()
def tests() -> None:
    pass


@tests.command()
def gui() -> None:
    """Run the GUI for tests."""

    env = {"CYPRESS_PATTY_UNIT_TESTING": "true"}

    if os.environ.get("DISPLAY") is None:
        env["DISPLAY"] = "host.docker.internal:0"
    else:
        env["DISPLAY"] = os.environ["DISPLAY"]

    # We may need to run "xhost +" before that
    compose.exec_in_frontend_container(["npx", "cypress", "open"], env=env)


@dev.group()
def fanout() -> None:
    pass


@fanout.command()
def reload() -> None:
    """Reload the fanout."""

    compose.run_or_exec_in_container("exec", "fanout", ["nginx", "-s", "reload"])
