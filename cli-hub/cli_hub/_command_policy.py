"""Convert remote registry commands into narrowly validated argv lists."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys


class RegistryCommandRejected(ValueError):
    """Raised when a registry command is outside the supported safe shapes."""


def run_command(command: str | list[str]) -> subprocess.CompletedProcess[str]:
    """Run explicit argv only; shell syntax is never interpreted."""
    try:
        argv = shlex.split(command) if isinstance(command, str) else list(command)
    except ValueError as exc:
        return subprocess.CompletedProcess(command, 126, "", f"Rejected command: {exc}")
    if not argv or any(token in {"|", "&&", "||", ";", ">", "<"} for token in argv):
        return subprocess.CompletedProcess(
            command, 126, "", "Rejected command: shell operators are not supported."
        )
    try:
        return subprocess.run(argv, capture_output=True, text=True)
    except FileNotFoundError as exc:
        missing = exc.filename or argv[0]
        return subprocess.CompletedProcess(command, 127, "", f"Command not found: {missing}")


def _parts(command: str) -> list[str]:
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        raise RegistryCommandRejected(f"invalid command quoting: {exc}") from exc
    if not parts:
        raise RegistryCommandRejected("empty registry command")
    return parts


def _brew_argv(parts: list[str], action: str) -> list[str]:
    verbs = {"install": "install", "uninstall": "uninstall", "update": "upgrade"}
    if len(parts) < 3 or os.path.basename(parts[0]) != "brew" or parts[1] != verbs[action]:
        raise RegistryCommandRejected(f"unsupported Homebrew {action} command")
    operands = parts[2:]
    if operands[:1] == ["--cask"]:
        operands = operands[1:]
    if len(operands) != 1 or operands[0].startswith("-"):
        raise RegistryCommandRejected("Homebrew commands must name exactly one formula or cask")
    return parts


def _pip_argv(parts: list[str], action: str) -> list[str]:
    if len(parts) < 5 or os.path.basename(parts[0]) not in {"python", "python3"}:
        raise RegistryCommandRejected(f"unsupported pip {action} command")
    if parts[1:3] != ["-m", "pip"]:
        raise RegistryCommandRejected(f"unsupported pip {action} command")

    expected = {
        "install": ["install"],
        "uninstall": ["uninstall", "-y"],
        "update": ["install", "--upgrade", "--force-reinstall"],
    }[action]
    if parts[3:-1] != expected or parts[-1].startswith("-"):
        raise RegistryCommandRejected(
            "pip registry commands must use the approved action flags and exactly one package"
        )
    return [sys.executable, *parts[1:]]


def registry_command_argv(cli: dict, action: str) -> list[str]:
    """Return safe argv for a remote registry action, or reject it.

    Script installers are intentionally manual: consent does not make piping an
    unaudited network response into a shell a trustworthy installation path.
    """
    command = cli.get(f"{action}_cmd")
    if not command:
        raise RegistryCommandRejected(f"no {action} command is defined")
    manager = cli.get("package_manager")
    if manager == "script":
        raise RegistryCommandRejected(
            "automatic script installers are disabled; inspect the publisher's instructions manually"
        )
    parts = _parts(command)
    if manager == "brew":
        return _brew_argv(parts, action)
    if manager == "pip":
        return _pip_argv(parts, action)
    raise RegistryCommandRejected(f"unsupported registry package manager: {manager or 'unspecified'}")
