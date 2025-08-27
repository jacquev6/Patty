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
    build("pre-warm", "pre-warm")


@prod.command()
def preview() -> None:
    print("Patty prod preview: build")
    build("preview", "load")
    subprocess.run(["docker", "compose", "build"], cwd="support/prod", check=True)
    print("Patty prod preview: pull")
    subprocess.run(["docker", "compose", "pull", "--ignore-buildable"], cwd="support/prod", check=True)
    print("Patty prod preview: start")
    try:
        subprocess.run(
            ["docker", "compose", "up", "--no-build", "--pull", "never", "--remove-orphans", "--detach"],
            cwd="support/prod",
            check=True,
        )
        print("Patty prod preview: started (close with Ctrl+C)")
        try:
            subprocess.run(["docker", "compose", "logs", "--follow"], cwd="support/prod", check=False)
        except KeyboardInterrupt:
            pass
    finally:
        print("Patty prod preview: clean-up")
        subprocess.run(["docker", "compose", "down", "--remove-orphans"], cwd="support/prod", check=True)
        subprocess.run(["docker", "compose", "rm", "--stop", "--volumes", "--force"], cwd="support/prod", check=True)


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
    build(patty_version, "push")
    subprocess.run(["git", "tag", patty_version], check=True)
    subprocess.run(["git", "push", "origin", "main", "--tags"], check=True)

    # Continue working
    subprocess.run(["git", "checkout", "develop"], check=True)
    subprocess.run(["git", "merge", "main"], check=True)
    subprocess.run(["git", "push", "origin", "develop"], check=True)


def build(patty_version: str, action: typing.Literal["pre-warm", "push", "load"]) -> None:
    options = {
        "pre-warm": ["--pull", "--platform", "linux/amd64,linux/arm64"],
        "push": ["--platform", "linux/amd64,linux/arm64", "--push"],
        "load": ["--platform", "linux/amd64", "--load"],
    }

    if action != "pre-warm":
        subprocess.run(["./dev.sh", "clean", "--force"])

    builders = subprocess.run(
        ["docker", "buildx", "ls"], check=True, capture_output=True, universal_newlines=True
    ).stdout
    if "patty-multi-platform-builder" not in builders:
        subprocess.run(["docker", "buildx", "create", "--name", "patty-multi-platform-builder"], check=True)

    if action == "pre-warm":
        part_pattern = re.compile(r"^FROM .* AS (?P<target>(?P<part>\S+)-dependencies)$")
    else:
        part_pattern = re.compile(r"^FROM .* AS (?P<target>final-(?P<part>\S+))$")

    with open("support/prod/docker/Dockerfile") as f:
        parts = []
        for line in f:
            if m := part_pattern.match(line):
                parts.append((m.group("part"), m.group("target")))

    for part, target in parts:
        print(part)
        print("-" * len(part))
        subprocess.run(
            [
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
                "--build-arg",
                f"PATTY_VERSION={patty_version}",
                "--tag",
                f"jacquev6/patty:{patty_version}-{part}",
                *options[action],
            ],
            check=True,
        )


@prod.command()
@click.argument("args", nargs=-1)
def compose(args: tuple[str, ...]) -> None:
    subprocess.run(["docker", "compose"] + list(args), cwd="support/prod", check=True)
