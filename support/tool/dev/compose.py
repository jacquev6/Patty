import itertools
import shlex
import subprocess
import typing


def exec_alembic(command: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    return exec_in_backend_container(command=["alembic"] + command, workdir="/app/backend/patty", capture=capture)


def exec_in_backend_container(
    command: list[str],
    *,
    env: dict[str, str] = {},
    workdir: str | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return run_or_exec_in_container(
        run_or_exec="exec",
        container="backend-shell",
        command=command,
        env=env,
        workdir=workdir,
        check=check,
        capture=capture,
    )


def exec_in_frontend_container(
    command: list[str],
    *,
    env: dict[str, str] = {},
    workdir: str | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return run_or_exec_in_container(
        run_or_exec="exec",
        container="frontend-shell",
        command=command,
        env=env,
        workdir=workdir,
        check=check,
        capture=capture,
    )


def run_in_frontend_container(
    command: list[str],
    *,
    env: dict[str, str] = {},
    workdir: str | None = None,
    check: bool = True,
    capture: bool = False,
    mount: dict[str, str] = {},
    quiet: bool = False,
) -> subprocess.CompletedProcess[str]:
    return run_or_exec_in_container(
        run_or_exec="run",
        container="frontend-shell",
        command=command,
        env=env,
        workdir=workdir,
        check=check,
        capture=capture,
        mount=mount,
        quiet=quiet,
    )


def run_or_exec_in_container(
    run_or_exec: typing.Literal["run", "exec"],
    container: str,
    command: list[str],
    env: dict[str, str] = {},
    workdir: str | None = None,
    check: bool = True,
    capture: bool = False,
    mount: dict[str, str] = {},
    quiet: bool = False,
) -> subprocess.CompletedProcess[str]:
    if workdir is None:
        workdir_options = []
        workdir_string = ""
    else:
        workdir_options = ["--workdir", workdir]
        workdir_string = f":{workdir}"

    if mount:
        mount_options = list(itertools.chain.from_iterable(("--volume", f"{src}:{dst}") for src, dst in mount.items()))
        mount_string = f" with mounts {' '.join(f'{src}:{dst}' for src, dst in mount.items())}"
    else:
        mount_options = []
        mount_string = ""

    env_options = list(itertools.chain.from_iterable(("--env", f"{k}={v}") for k, v in env.items()))
    if len(env) == 0:
        env_string = ""
    else:
        env_string = f" with environment {' '.join(f'{k}={v}' for k, v in env.items())}"

    if capture:
        capture_string = ", capturing output"
    else:
        capture_string = ""

    if not quiet:
        print(
            f"{run_or_exec.title()}-ing {shlex.join(command)!r} in {container}{workdir_string}{mount_string}{env_string}{capture_string}"
        )

    return subprocess.run(
        ["docker", "compose", run_or_exec] + env_options + workdir_options + mount_options + [container] + command,
        cwd="support/dev-env",
        check=check,
        universal_newlines=True,
        capture_output=capture,
    )
