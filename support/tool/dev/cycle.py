import dataclasses
import glob
import os
import subprocess

from .compose import run_alembic, run_in_backend_container, run_in_frontend_container


class DevelopmentCycleError(Exception):
    pass


@dataclasses.dataclass
class DevelopmentCycle:
    do_migration: bool
    cost_money: bool
    do_backend: bool
    do_frontend: bool
    do_end_to_end: bool
    do_format: bool
    do_lint: bool
    do_type_check: bool
    do_test: bool
    frontend_specs: list[str] | None
    end_to_end_specs: list[str] | None
    browsers: list[str]

    def run(self) -> None:
        try:
            self.do_run()
        except subprocess.CalledProcessError as e:
            raise DevelopmentCycleError()

    def do_run(self) -> None:
        if self.do_backend:
            if self.do_migration:
                run_in_backend_container(
                    ["python", "-m", "patty", "restore-database", "--yes", "--patch-according-to-settings"]
                )
                existing = glob.glob("backend/patty/migrations/versions/*_dev.py")
                assert len(existing) <= 1
                if len(existing) == 1:
                    rev_id_options = ["--rev-id", os.path.basename(existing[0])[:-7]]
                    os.unlink(existing[0])
                else:
                    rev_id_options = []
                current = run_alembic(["current"], capture=True).stdout.split(" ")[0]
                expected = run_alembic(["show", "head"], capture=True).stdout.splitlines()[0].split(" ")[1]
                if current != expected:
                    print(
                        f"Current migration {current} does not match expected migration {expected}. Maybe you need to load a more recent backup?"
                    )
                    raise DevelopmentCycleError()
                run_alembic(["revision", "--autogenerate", "-m", "dev"] + rev_id_options)
                input("Check (and fix) the generated migration file. Press enter to continue")
                run_alembic(["upgrade", "head"])
                run_in_backend_container(["python", "-m", "patty", "migrate-data"])

            if self.do_format:
                run_in_backend_container(
                    ["black", "backend", "support/tool", "--line-length", "120", "--skip-magic-trailing-comma"],
                    workdir="/app",
                )

            if self.do_lint:
                pass  # @todo Investigate linters for Python code (e.g. PyLint, ruff)

            if self.do_type_check:
                run_in_backend_container(["mypy", "backend", "support/tool", "--strict"], workdir="/app")

            if self.do_test:
                env: dict[str, str] = {}
                if self.cost_money:
                    env["PATTY_TESTS_SPEND_MONEY"] = "true"
                if not self.do_migration:
                    env["PATTY_TESTS_SKIP_MIGRATIONS"] = "true"

                run_in_backend_container(["python", "-m", "unittest", "discover", "--pattern", "*.py"], env=env)

        if self.do_frontend:
            if self.do_format:
                run_in_frontend_container(["npm", "run", "format"])

            if self.do_lint:
                for file in glob.glob("**/*.cy.ts", recursive=True):
                    try:
                        with open(file, "r") as f:
                            for lineIndex, line in enumerate(f):
                                if ".skip" in line or ".only" in line:
                                    print(f"{file}:{lineIndex+1} {line.strip()}")
                                    exit(1)
                    except IsADirectoryError:
                        pass
                run_in_frontend_container(["npm", "run", "lint"])

            if self.do_type_check:
                run_in_frontend_container(["npm", "run", "type-check"])

            if self.do_test:
                if self.frontend_specs is None:
                    specs = []
                else:
                    specs = ["--spec", ",".join(self.frontend_specs)]

                for browser in self.browsers:
                    run_in_frontend_container(
                        ["npx", "cypress", "run", "--component", "--browser", browser] + specs,
                        env={"PATTY_UNIT_TESTING": "true"},
                    )

        if self.do_end_to_end:
            if self.do_test:
                if self.end_to_end_specs is None:
                    specs = []
                else:
                    specs = ["--spec", ",".join(self.end_to_end_specs)]
                for browser in self.browsers:
                    run_in_frontend_container(["npx", "cypress", "run", "--e2e", "--browser", browser] + specs)
