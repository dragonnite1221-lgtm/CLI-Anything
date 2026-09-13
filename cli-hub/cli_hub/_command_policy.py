"""Convert remote registry commands into narrowly validated argv lists."""

from __future__ import annotations

import os
import shlex
import shutil
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


def _uv_argv(parts: list[str], action: str, uv_executable: str) -> list[str]:
    # parts[0] must be the exact literal "uv" (no path separators): a basename-only
    # check would let a registry entry smuggle an arbitrary binary via "./uv" or
    # "/attacker/dir/uv". The trusted, PATH-resolved executable is substituted in.
    verbs = {"install": "install", "uninstall": "uninstall", "update": "upgrade"}
    if (
        len(parts) < 4
        or parts[0] != "uv"
        or parts[1] != "tool"
        or parts[2] != verbs[action]
    ):
        raise RegistryCommandRejected(f"unsupported uv {action} command")
    operands = parts[3:]
    if len(operands) != 1 or operands[0].startswith("-"):
        raise RegistryCommandRejected("uv tool commands must name exactly one package or source")
    return [uv_executable, *parts[1:]]


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


def registry_command_argv(
    cli: dict, action: str, *, uv_executable: str | None = None
) -> list[str]:
    """Return safe argv for a remote registry action, or reject it.

    Script installers are intentionally manual: consent does not make piping an
    unaudited network response into a shell a trustworthy installation path.

    ``uv_executable`` should be the caller's already-resolved, trusted path to
    the ``uv`` binary (e.g. from ``shutil.which("uv")``); it is substituted in
    place of whatever the registry command string named. It falls back to a
    fresh PATH lookup when the caller doesn't supply one.
    """
    command = cli.get(f"{action}_cmd")
    if not command:
        raise RegistryCommandRejected(f"no {action} command is defined")
    # A registry entry may set install_strategy="uv"/"pip" without repeating an
    # identical package_manager; fall back so it still resolves to that manager
    # instead of being rejected as unspecified (CLI-Anything-1 P2 regression).
    manager = cli.get("package_manager") or cli.get("install_strategy")
    if manager == "script":
        raise RegistryCommandRejected(
            "automatic script installers are disabled; inspect the publisher's instructions manually"
        )
    parts = _parts(command)
    if manager == "brew":
        return _brew_argv(parts, action)
    if manager == "pip":
        return _pip_argv(parts, action)
    if manager == "uv":
        resolved_uv = uv_executable or shutil.which("uv")
        if not resolved_uv:
            raise RegistryCommandRejected("uv executable was not found on PATH")
        return _uv_argv(parts, action, resolved_uv)
    raise RegistryCommandRejected(f"unsupported registry package manager: {manager or 'unspecified'}")
