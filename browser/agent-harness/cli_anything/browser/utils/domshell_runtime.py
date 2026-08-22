"""Install and verify the local, lockfile-pinned DOMShell server runtime."""

from __future__ import annotations

from importlib import resources
import json
import os
from pathlib import Path
import shutil
import subprocess


RUNTIME_ENV = "CLI_ANYTHING_DOMSHELL_RUNTIME_DIR"
PACKAGE_NAME = "@apireno/domshell"
PACKAGE_VERSION = "2.0.10"
RUNTIME_MARKER = ".cli-anything-domshell-runtime"
RUNTIME_MARKER_CONTENT = b"cli-anything-domshell-runtime-v1\n"


class DOMShellRuntimeError(RuntimeError):
    """The locally installed DOMShell runtime cannot be trusted or used."""


def runtime_dir() -> Path:
    """Return the owner-private directory containing the installed npm runtime."""

    configured = os.environ.get(RUNTIME_ENV)
    path = Path(configured).expanduser() if configured else Path.home() / ".local/share/cli-anything/domshell-runtime"
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise DOMShellRuntimeError("DOMShell runtime path must be a real directory")
        if path.stat().st_mode & 0o077:
            raise DOMShellRuntimeError("DOMShell runtime directory must not be group- or world-accessible")
    return path


def _bundled_file(name: str) -> bytes:
    try:
        return resources.files("cli_anything.browser").joinpath("vendor", "domshell", name).read_bytes()
    except (FileNotFoundError, ModuleNotFoundError, OSError) as error:
        raise DOMShellRuntimeError("Bundled DOMShell lockfile is unavailable") from error


def _write_private_file(path: Path, payload: bytes) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(payload)
    temporary.chmod(0o600)
    temporary.replace(path)


def _node() -> str:
    executable = shutil.which("node")
    if not executable:
        raise DOMShellRuntimeError("Node.js 18 or later is required for the locally installed DOMShell runtime")
    return executable


def _assert_private(path: Path) -> None:
    try:
        if path.stat().st_mode & 0o022:
            raise DOMShellRuntimeError(f"DOMShell runtime file is group- or world-writable: {path.name}")
    except FileNotFoundError as error:
        raise DOMShellRuntimeError("DOMShell runtime is not installed; run `cli-anything-browser secure install`") from error


def _prepare_install_root() -> Path:
    """Create a dedicated install root without letting npm touch another project."""

    root = runtime_dir()
    if not root.exists():
        root.mkdir(mode=0o700, parents=True)
    root.chmod(0o700)
    marker = root / RUNTIME_MARKER
    if marker.exists():
        _assert_private(marker)
        if marker.read_bytes() != RUNTIME_MARKER_CONTENT:
            raise DOMShellRuntimeError("DOMShell runtime marker is invalid; refusing to replace this directory")
    elif any(root.iterdir()):
        raise DOMShellRuntimeError(
            "DOMShell runtime directory is not empty and is not managed by this CLI; refusing to run npm there"
        )
    else:
        _write_private_file(marker, RUNTIME_MARKER_CONTENT)
    return root


def _installed_package() -> Path:
    root = runtime_dir()
    if not root.exists():
        raise DOMShellRuntimeError("DOMShell runtime is not installed; run `cli-anything-browser secure install`")
    if root.stat().st_mode & 0o077:
        raise DOMShellRuntimeError("DOMShell runtime directory must not be group- or world-accessible")
    marker = root / RUNTIME_MARKER
    _assert_private(marker)
    if marker.read_bytes() != RUNTIME_MARKER_CONTENT:
        raise DOMShellRuntimeError("DOMShell runtime marker is invalid; reinstall it")
    lock_path = root / "package-lock.json"
    _assert_private(lock_path)
    if lock_path.read_bytes() != _bundled_file("package-lock.json"):
        raise DOMShellRuntimeError("DOMShell runtime lockfile does not match the bundled verified lockfile; reinstall it")
    package = root / "node_modules" / "@apireno" / "domshell"
    _assert_private(package)
    manifest = package / "package.json"
    _assert_private(manifest)
    try:
        metadata = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise DOMShellRuntimeError("Installed DOMShell package metadata is unreadable") from error
    if metadata.get("name") != PACKAGE_NAME or metadata.get("version") != PACKAGE_VERSION:
        raise DOMShellRuntimeError("Installed DOMShell package does not match the verified version; reinstall it")
    return package


def command(binary: str, *arguments: str) -> list[str]:
    """Build a network-free Node command for a verified local DOMShell binary."""

    if binary not in {"domshell", "domshell-proxy"}:
        raise ValueError("Unsupported DOMShell binary")
    package = _installed_package()
    script = package / "bin" / f"{binary}.js"
    _assert_private(script)
    if not script.resolve().is_relative_to(package.resolve()):
        raise DOMShellRuntimeError("DOMShell binary escapes the verified runtime directory")
    return [_node(), str(script), *arguments]


def install() -> Path:
    """Install exactly the bundled lockfile with npm integrity checks and no scripts."""

    root = _prepare_install_root()
    _write_private_file(root / "package.json", _bundled_file("package.json"))
    _write_private_file(root / "package-lock.json", _bundled_file("package-lock.json"))
    npm = shutil.which("npm")
    if not npm:
        raise DOMShellRuntimeError("npm is required to install the locked DOMShell runtime")
    environment = {"PATH": os.environ.get("PATH", ""), "HOME": str(Path.home()), "npm_config_ignore_scripts": "true"}
    try:
        subprocess.run(
            [npm, "ci", "--ignore-scripts", "--omit=dev", "--no-audit", "--fund=false"],
            cwd=root,
            env=environment,
            check=True,
            timeout=180,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise DOMShellRuntimeError("Locked DOMShell runtime installation failed") from error
    _installed_package()
    return root


def status() -> dict[str, object]:
    """Return a non-secret installation readiness summary."""

    try:
        package = _installed_package()
        return {"installed": True, "runtime": str(runtime_dir()), "package": str(package), "version": PACKAGE_VERSION}
    except DOMShellRuntimeError as error:
        return {"installed": False, "reason": str(error)}
