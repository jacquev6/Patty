import itertools
import shlex
import subprocess


def run_alembic(command: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    return run_in_backend_container(command=["alembic"] + command, workdir="/app/backend/patty", capture=capture)


def run_in_backend_container(
    command: list[str],
    *,
    env: dict[str, str] = {},
    workdir: str | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return run_in_container(
        container="backend-shell", command=command, env=env, workdir=workdir, check=check, capture=capture
    )


def run_in_frontend_container(
    command: list[str],
    *,
    env: dict[str, str] = {},
    workdir: str | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return run_in_container(
        container="frontend-shell", command=command, env=env, workdir=workdir, check=check, capture=capture
    )


def run_in_container(
    container: str,
    command: list[str],
    env: dict[str, str] = {},
    workdir: str | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    if workdir is None:
        workdir_options = []
        workdir_string = ""
    else:
        workdir_options = ["--workdir", workdir]
        workdir_string = f":{workdir}"

    env_options = list(itertools.chain.from_iterable(("--env", f"{k}={v}") for k, v in env.items()))
    if len(env) == 0:
        env_string = ""
    else:
        env_string = f" with environment {' '.join(f'{k}={v}' for k, v in env.items())}"

    print(f"Running {shlex.join(command)!r} in {container}{workdir_string}{env_string}")

    return subprocess.run(
        ["docker", "compose", "exec"] + env_options + workdir_options + [container] + command,
        cwd="support/dev-env",
        check=check,
        universal_newlines=True,
        capture_output=capture,
    )


def stop(container: str) -> None:
    subprocess.run(["docker", "compose", "stop", container], cwd="support/dev-env", check=True)


def restart(container: str) -> None:
    subprocess.run(["docker", "compose", "restart", container], cwd="support/dev-env", check=True)
