# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import datetime
import glob
import os
import re
import subprocess
import typing

import click

from ..main_command import main


@main.group()
def prod() -> None:
    pass


@prod.command()
def pre_warm_build_cache() -> None:
    print("Patty prod pre-warm: build")
    build(patty_version=None, action="pre-warm")


@prod.command()
@click.option("--with-jacquev6-s3", is_flag=True, default=False, hidden=True)
def preview(with_jacquev6_s3: bool) -> None:
    env = os.environ.copy()
    env["PATTY_USE_JACQUEV6_S3"] = "true" if with_jacquev6_s3 else "false"

    print("Patty prod preview: build")
    build(patty_version="preview", action="load")
    subprocess.run(["docker", "compose", "build"], cwd="support/prod", env=env, check=True)
    print("Patty prod preview: pull")
    subprocess.run(["docker", "compose", "pull", "--ignore-buildable"], cwd="support/prod", env=env, check=True)
    print("Patty prod preview: start")
    try:
        subprocess.run(
            ["docker", "compose", "up", "--no-build", "--pull", "never", "--remove-orphans", "--detach"],
            cwd="support/prod",
            env=env,
            check=True,
        )
        print("Patty prod preview: started (close with Ctrl+C)")
        try:
            subprocess.run(["docker", "compose", "logs", "--follow"], cwd="support/prod", env=env, check=False)
        except KeyboardInterrupt:
            pass
    finally:
        print("Patty prod preview: clean-up")
        subprocess.run(["docker", "compose", "down", "--remove-orphans"], cwd="support/prod", env=env, check=True)
        subprocess.run(
            ["docker", "compose", "rm", "--stop", "--volumes", "--force"], cwd="support/prod", env=env, check=True
        )


@prod.command()
def publish() -> None:
    # Check cleanliness

    if (
        subprocess.run(
            ["git", "branch", "--show-current"], check=True, capture_output=True, universal_newlines=True
        ).stdout.strip()
        != "main"
    ):
        print("Not on branch 'main'.")
        raise click.Abort()
    if (
        subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
            universal_newlines=True,
        ).stdout.strip()
        != ""
    ):
        subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], check=True)
        print("Untracked files.")
        raise click.Abort()
    if subprocess.run(["git", "diff", "--stat", "--exit-code"], check=False).returncode != 0:
        print("Unstaged changes.")
        raise click.Abort()
    if subprocess.run(["git", "diff", "--stat", "--staged", "--exit-code"], check=False).returncode != 0:
        input(
            "Staged-but-not-committed changes will be included in publication commit. Press enter to continue, Ctrl+C to abort."
        )

    # Prepare

    patty_version = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    print(patty_version)

    dev_migrations = glob.glob("backend/patty/migrations/versions/*_dev.py")
    if len(dev_migrations) > 1:
        print("More than one dev migration found.")
        raise click.Abort()
    elif len(dev_migrations) == 1:
        dev_migration = dev_migrations[0]
        os.rename(dev_migration, dev_migration.replace("_dev.py", f"_version-{patty_version}.py"))

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", f"Publish version {patty_version}"], check=True)

    # Build and publish
    build(patty_version=patty_version, action="push")
    subprocess.run(["git", "tag", patty_version], check=True)
    subprocess.run(["git", "push", "origin", "main", "--tags"], check=True)

    # Continue working
    subprocess.run(["git", "checkout", "develop"], check=True)
    subprocess.run(["git", "merge", "main"], check=True)
    subprocess.run(["git", "push", "origin", "develop"], check=True)


Action = typing.Literal["pre-warm", "push", "load"]


def build(*, patty_version: str | None, action: Action) -> None:
    if action != "pre-warm":
        subprocess.run(["./dev.sh", "clean", "--force"])

    builders = subprocess.run(
        ["docker", "buildx", "ls"], check=True, capture_output=True, universal_newlines=True
    ).stdout
    if "patty-multi-platform-builder" not in builders:
        subprocess.run(["docker", "buildx", "create", "--name", "patty-multi-platform-builder"], check=True)

    for part, target in find_parts(action):
        print(part)
        print("-" * len(part))
        subprocess.run(
            make_build_command(patty_version=patty_version, target=target, part=part, action=action), check=True
        )


def find_parts(action: Action) -> typing.Iterable[tuple[str, str]]:
    if action == "pre-warm":
        part_pattern = re.compile(r"^FROM .* AS (?P<target>(?P<part>\S+)-dependencies)$")
    else:
        part_pattern = re.compile(r"^FROM .* AS (?P<target>final-(?P<part>\S+))$")

    with open("support/prod/docker/Dockerfile") as f:
        for line in f:
            if m := part_pattern.match(line):
                yield (m.group("part"), m.group("target"))


def make_build_command(*, patty_version: str | None, target: str, part: str, action: Action) -> list[str]:
    command = [
        "docker",
        "buildx",
        "build",
        "--builder",
        "patty-multi-platform-builder",
        ".",
        "--file",
        "support/prod/docker/Dockerfile",
        "--target",
        target,
        "--pull",
        "--no-cache",
    ]

    if patty_version is None:
        assert action == "pre-warm"
    else:
        command += ["--build-arg", f"PATTY_VERSION={patty_version}", "--tag", f"jacquev6/patty:{patty_version}-{part}"]

    if action == "pre-warm":
        command += ["--tag", f"jacquev6/patty:latest-{part}-dependencies", "--push"]
    else:
        command += [
            "--build-arg",
            "FRONTEND_DEPENDENCIES_IMAGE=jacquev6/patty:latest-frontend-dependencies",
            "--build-arg",
            "BACKEND_DEPENDENCIES_IMAGE=jacquev6/patty:latest-backend-dependencies",
        ]

    if action == "pre-warm":
        command += ["--platform", "linux/amd64,linux/arm64"]
    elif action == "push":
        command += ["--platform", "linux/amd64,linux/arm64", "--push"]
    elif action == "load":
        command += ["--platform", "linux/amd64", "--load"]
    else:
        assert False

    return command


@prod.command()
@click.argument("args", nargs=-1)
def compose(args: tuple[str, ...]) -> None:
    env = os.environ.copy()
    env["PATTY_USE_JACQUEV6_S3"] = "false"
    subprocess.run(["docker", "compose"] + list(args), cwd="support/prod", env=env, check=True)
