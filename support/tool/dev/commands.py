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
                "backend/",
                "frontend/",
                "support/dev-env/backend/pip-packages/",
                "support/dev-env/db/backups/",
                "support/dev-env/frontend/cache/",
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
@click.argument("fixtures", nargs=-1)
def load_fixtures(fixtures: tuple[str, ...]) -> None:
    compose.run_in_backend_container(["python", "-m", "patty", "load-fixtures"] + list(fixtures), check=True)


@dev.command()
@click.option("--cost-money", is_flag=True)
@click.option("--only-backend", is_flag=True)
@click.option("--skip-backend", is_flag=True)
@click.option("--only-frontend", is_flag=True)
@click.option("--skip-frontend", is_flag=True)
@click.option("--only-e2e", is_flag=True)
@click.option("--skip-e2e", is_flag=True)
@click.option("--only-migration", is_flag=True)
@click.option("--skip-migration", is_flag=True)
@click.option("--only-format", is_flag=True)
@click.option("--skip-format", is_flag=True)
@click.option("--only-lint", is_flag=True)
@click.option("--skip-lint", is_flag=True)
@click.option("--only-type-check", is_flag=True)
@click.option("--skip-type-check", is_flag=True)
@click.option("--only-test", is_flag=True)
@click.option("--skip-test", is_flag=True)
@click.option("--only-spec", type=str, multiple=True)
@click.option("--only-electron", is_flag=True)
@click.option("--skip-electron", is_flag=True)
@click.option("--only-chromium", is_flag=True)
@click.option("--skip-chromium", is_flag=True)
@click.option("--only-firefox", is_flag=True)
@click.option("--skip-firefox", is_flag=True)
def cycle(
    cost_money: bool,
    only_backend: bool,
    skip_backend: bool,
    only_frontend: bool,
    skip_frontend: bool,
    only_e2e: bool,
    skip_e2e: bool,
    only_migration: bool,
    skip_migration: bool,
    only_format: bool,
    skip_format: bool,
    only_lint: bool,
    skip_lint: bool,
    only_type_check: bool,
    skip_type_check: bool,
    only_test: bool,
    skip_test: bool,
    only_spec: tuple[str, ...],
    only_electron: bool,
    skip_electron: bool,
    only_chromium: bool,
    skip_chromium: bool,
    only_firefox: bool,
    skip_firefox: bool,
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

    frontend_specs: list[str] | None = []
    assert isinstance(frontend_specs, list)
    end_to_end_specs: list[str] | None = []
    assert isinstance(end_to_end_specs, list)
    for spec in only_spec:
        if spec.startswith("frontend/src") and spec.endswith(".cy.ts"):
            frontend_specs.append(spec[9:])
        elif spec.startswith("frontend/e2e-tests") and spec.endswith(".cy.ts"):
            end_to_end_specs.append(spec[9:])
        else:
            raise ValueError(f"Invalid spec: {spec}")
    if len(frontend_specs) == 0:
        frontend_specs = None
    if len(end_to_end_specs) == 0:
        end_to_end_specs = None

    cycle = DevelopmentCycle(
        do_migration=do_migration,
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
    )
    try:
        cycle.run()
    except DevelopmentCycleError as e:
        raise click.Abort()


@dev.group()
def tests() -> None:
    pass


@tests.command()
def gui() -> None:
    """Run the GUI for tests."""

    env = {"PATTY_UNIT_TESTING": "true"}

    if os.environ.get("DISPLAY") is None:
        env["DISPLAY"] = "host.docker.internal:0"
    else:
        env["DISPLAY"] = os.environ["DISPLAY"]

    # We may need to run "xhost +" before that
    compose.run_in_frontend_container(["npx", "cypress", "open"], env=env)


@tests.command()
def visual_diff() -> None:
    # @todo Use 'webbrowser.open' to open the report at 'http://127.0.0.1:6868'
    compose.run_in_frontend_container(["npx", "cypress-image-diff-html-report", "start"], check=False)


@dev.group()
def fanout() -> None:
    pass


@fanout.command()
def reload() -> None:
    """Reload the fanout."""

    compose.run_in_container("fanout", ["nginx", "-s", "reload"])


@dev.command()
@click.option("--restore/--no-restore", is_flag=True, default=True)
def investigate_issue_39(restore: bool) -> None:
    # Outputs of actual runs of this script are in comments in https://github.com/jacquev6/Patty/issues/39

    reference_batch_id = "46"
    count = "50"

    if restore:
        backup_to_load = "s3://jacquev6/patty/prod/backups/patty-backup-20250512-051611.tar.gz"
        compose.run_in_backend_container(
            ["python", "-m", "patty", "restore-database", "--yes", "--patch-according-to-settings", backup_to_load]
        )
        compose.run_alembic(["upgrade", "head"])

    compose.stop("submission-daemon")

    for parallel in ["1", "10"]:
        compose.run_in_backend_container(
            ["python", "-m", "patty", "investigate-issue-39", reference_batch_id, count, parallel, "1"]
        )


@dev.group()
def submission_daemon() -> None:
    pass


@submission_daemon.command(name="reload")
def reload_submission_daemon() -> None:
    compose.restart("submission-daemon")
