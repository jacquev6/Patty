import dataclasses
import glob
import itertools
import os
import shutil
import subprocess
import typing

import joblib

from .compose import exec_alembic, exec_in_backend_container, exec_in_frontend_container, run_in_frontend_container


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
    frontend_specs: list[str]
    end_to_end_specs: list[str]
    browsers: list[str]
    accept_visual_diffs: bool

    def run(self) -> None:
        try:
            self.do_run()
        except subprocess.CalledProcessError:
            raise DevelopmentCycleError()

    def do_run(self) -> None:
        if self.do_backend:
            if self.do_migration:
                exec_in_backend_container(
                    ["python", "-m", "patty", "restore-database", "--yes", "--patch-according-to-settings"]
                )
                existing = glob.glob("backend/patty/migrations/versions/*_dev.py")
                assert len(existing) <= 1
                if len(existing) == 1:
                    rev_id_options = ["--rev-id", os.path.basename(existing[0])[:-7]]
                    os.unlink(existing[0])
                else:
                    rev_id_options = []
                current = exec_alembic(["current"], capture=True).stdout.split(" ")[0]
                expected = exec_alembic(["show", "head"], capture=True).stdout.splitlines()[0].split(" ")[1]
                if current != expected:
                    print(
                        f"Current migration {current} does not match expected migration {expected}. Maybe you need to load a more recent backup?"
                    )
                    raise DevelopmentCycleError()
                exec_alembic(["revision", "--autogenerate", "-m", "dev"] + rev_id_options)
                input("Check (and fix) the generated migration file. Press enter to continue")
                exec_alembic(["upgrade", "head"])
                exec_in_backend_container(["python", "-m", "patty", "migrate-data"])

            if self.do_format:
                exec_in_backend_container(
                    ["black", "backend", "support/tool", "--line-length", "120", "--skip-magic-trailing-comma"],
                    workdir="/app",
                )

            if self.do_lint:
                exec_in_backend_container(["ruff", "check", "backend", "support/tool", "--fix"], workdir="/app")

            if self.do_type_check:
                exec_in_backend_container(["mypy", "backend", "support/tool", "--strict"], workdir="/app")

            if self.do_test:
                env: dict[str, str] = {}
                if self.cost_money:
                    env["PATTY_TESTS_SPEND_MONEY"] = "true"
                if not self.do_migration:
                    env["PATTY_TESTS_SKIP_MIGRATIONS"] = "true"

                exec_in_backend_container(
                    ["python", "-m", "doctest", "--option", "ELLIPSIS", "generated/patty_json_to_html.py"], env=env
                )
                exec_in_backend_container(["python", "-m", "unittest", "discover", "--pattern", "*.py"], env=env)

        if self.do_frontend:
            if self.do_format:
                exec_in_frontend_container(["npx", "prettier", "--write", "src/", "e2e-tests/"])

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
                exec_in_frontend_container(["npx", "eslint", ".", "--ignore-pattern", "**/*.min.js", "--fix"])

            if self.do_type_check:
                exec_in_frontend_container(["npx", "vue-tsc", "--build"])

            if self.do_test:
                jobs: list[dict[str, typing.Any]] = []
                for browser in self.browsers:
                    for spec in self.frontend_specs:
                        mounts = make_screenshots_directory(spec, browser, clear=self.accept_visual_diffs)
                        jobs.append(
                            dict(
                                command=[
                                    "npx",
                                    "cypress",
                                    "run",
                                    "--headless",
                                    "--component",
                                    "--browser",
                                    browser,
                                    "--spec",
                                    spec[9:],
                                ],
                                env={"PATTY_UNIT_TESTING": "true"},
                                check=False,
                                capture=True,
                                mount=mounts,
                                quiet=True,
                            )
                        )

                component_failures: list[subprocess.CompletedProcess[str]] = []
                result: subprocess.CompletedProcess[str]
                for result in joblib.Parallel(n_jobs=5, return_as="generator_unordered")(
                    joblib.delayed(run_in_frontend_container)(**job) for job in jobs
                ):
                    if result.returncode == 0:
                        print(f"{os.path.join('frontend', result.args[-1])} {result.args[-3]}: OK")
                    else:
                        component_failures.append(result)
                        print(f"{os.path.join('frontend', result.args[-1])} {result.args[-3]}: FAILED")

                for component_failure in component_failures:
                    print()
                    title = (
                        f"{os.path.join('frontend', component_failure.args[-1])} {component_failure.args[-3]}: FAILED"
                    )
                    print(title)
                    print("=" * len(title))
                    print(component_failure.stdout)
                    print(component_failure.stderr)

                maybe_remove_screenshots_directories(self.frontend_specs, self.browsers)

                if component_failures:
                    raise DevelopmentCycleError()

        if self.do_end_to_end:
            if self.do_test:
                try:
                    e2e_failures = list(
                        itertools.chain.from_iterable(
                            joblib.Parallel(n_jobs=1, return_as="list")(
                                joblib.delayed(run_e2e_tests)(
                                    self.end_to_end_specs, browser, clear=self.accept_visual_diffs
                                )
                                for browser in self.browsers
                            )
                        )
                    )

                    for e2e_failure in e2e_failures:
                        print()
                        print(e2e_failure)
                finally:
                    maybe_remove_screenshots_directories(self.end_to_end_specs, self.browsers)

                if e2e_failures:
                    raise DevelopmentCycleError()


def run_e2e_tests(specs: list[str], browser: str, clear: bool) -> list[str]:
    failures: list[str] = []
    for spec in specs:
        mounts = make_screenshots_directory(spec, browser, clear=clear)
        result = run_in_frontend_container(
            command=[
                "npx",
                "cypress",
                "run",
                "--e2e",
                "--browser",
                browser,
                "--config",
                "baseUrl=http://fanout:" + {"chromium": "8081", "electron": "8082", "firefox": "8083"}[browser],
                "--spec",
                spec[9:],
            ],
            check=False,
            capture=True,
            mount=mounts,
            quiet=True,
        )
        if result.returncode == 0:
            print(f"{spec} {browser}: OK")
        else:
            title = f"{spec} {browser}: FAILED"
            print(title)
            failures.append(f"{title}\n{'=' * len(title)}\n{result.stdout}\n{result.stderr}")
    return failures


def make_screenshots_directory(spec: str, browser: str, clear: bool) -> dict[str, str]:
    screenshots_path = os.path.join(os.path.abspath(spec) + ".screenshots", browser)
    if clear:
        shutil.rmtree(screenshots_path, ignore_errors=True)
    tmp_path = os.path.join(screenshots_path, "tmp")
    os.makedirs(tmp_path, exist_ok=True)
    html_report_path = os.path.join(screenshots_path, "html-report")
    os.makedirs(html_report_path, exist_ok=True)
    with open(os.path.join(screenshots_path, ".gitignore"), "w") as f:
        f.write("/comparison/\n/diff/\n/html-report/\n/tmp/\n")
    os.makedirs("frontend/cypress-image-diff-screenshots", exist_ok=True)
    os.makedirs("frontend/cypress-image-diff-html-report", exist_ok=True)
    os.makedirs("frontend/cypress/screenshots", exist_ok=True)
    return {
        screenshots_path: "/app/frontend/cypress-image-diff-screenshots",
        html_report_path: "/app/frontend/cypress-image-diff-html-report",
        tmp_path: "/app/frontend/cypress/screenshots",
    }


def maybe_remove_screenshots_directories(specs: typing.Iterable[str], browsers: typing.Iterable[str]) -> None:
    for spec in specs:
        for browser in browsers:
            screenshots_path = os.path.join(os.path.abspath(spec) + ".screenshots", browser)
            shutil.rmtree(os.path.join(screenshots_path, "tmp"), ignore_errors=True)
            baseline_path = os.path.join(screenshots_path, "baseline")
            if not os.path.isdir(baseline_path) or os.listdir(baseline_path) == []:
                shutil.rmtree(screenshots_path)
        if os.listdir(spec + ".screenshots") == []:
            shutil.rmtree(spec + ".screenshots")
    shutil.rmtree("frontend/cypress-image-diff-screenshots")
    shutil.rmtree("frontend/cypress-image-diff-html-report")
    shutil.rmtree("frontend/cypress/screenshots")
