# ruff: noqa: F403, F405, E501
from .installer_base import *  # noqa: F403

# fmt: off
from .installer_p1 import _UV_INSTALL_HINT, _find_npm, _find_uv, _run_command  # noqa: E402,E501
# fmt: on


def _bundled_uninstall(cli):
    note = cli.get("uninstall_notes") or (
        f"{cli['display_name']} is bundled with its parent app. "
        "Disable it in the upstream app or uninstall the parent app manually."
    )
    return False, note


def _bundled_update(cli):
    note = cli.get("update_notes") or (
        f"{cli['display_name']} is bundled with its parent app. "
        "Update the parent app to update this CLI."
    )
    return False, note


def _pip_install(cli):
    install_cmd = cli["install_cmd"]
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install"]
        + install_cmd.replace("pip install ", "").split(),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, f"Installed {cli['display_name']} ({cli['entry_point']})"
    return False, f"pip install failed:\n{result.stderr}"


def _pip_uninstall(cli):
    pkg_name = f"cli-anything-{cli['name']}"
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", pkg_name],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, f"Uninstalled {cli['display_name']}"
    return False, f"pip uninstall failed:\n{result.stderr}"


def _pip_update(cli):
    install_cmd = cli["install_cmd"]
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall"]
        + install_cmd.replace("pip install ", "").split(),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, f"Updated {cli['display_name']} to {cli['version']}"
    return False, f"Update failed:\n{result.stderr}"


def _uv_install(cli):
    if _find_uv() is None:
        return False, _UV_INSTALL_HINT
    result = _run_command(cli["install_cmd"])
    if result.returncode == 0:
        return True, f"Installed {cli['display_name']} ({cli['entry_point']})"
    return False, f"uv install failed:\n{result.stderr or result.stdout}"


def _uv_uninstall(cli):
    if _find_uv() is None:
        return False, _UV_INSTALL_HINT
    uninstall_cmd = cli.get("uninstall_cmd")
    if not uninstall_cmd:
        return False, f"No uninstall command is defined for {cli['display_name']}."
    result = _run_command(uninstall_cmd)
    if result.returncode == 0:
        return True, f"Uninstalled {cli['display_name']}"
    return False, f"uv uninstall failed:\n{result.stderr or result.stdout}"


def _uv_update(cli):
    if _find_uv() is None:
        return False, _UV_INSTALL_HINT
    update_cmd = cli.get("update_cmd")
    if not update_cmd:
        return False, f"No update command is defined for {cli['display_name']}."
    result = _run_command(update_cmd)
    if result.returncode == 0:
        return True, f"Updated {cli['display_name']}"
    return False, f"uv update failed:\n{result.stderr or result.stdout}"


def _npm_install(cli):
    npm = _find_npm()
    if npm is None:
        return False, (
            "npm is not installed. Install Node.js first:\n"
            "  macOS: brew install node\n"
            "  Linux: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs\n"
            "  Windows: Download from https://nodejs.org"
        )
    result = subprocess.run(
        [npm, "install", "-g", cli["npm_package"]], capture_output=True, text=True
    )
    if result.returncode == 0:
        return True, f"Installed {cli['display_name']} ({cli['entry_point']})"
    return False, f"npm install failed:\n{result.stderr}"


def _npm_uninstall(cli):
    npm = _find_npm()
    if npm is None:
        return False, "npm is not installed."
    result = subprocess.run(
        [npm, "uninstall", "-g", cli["npm_package"]], capture_output=True, text=True
    )
    if result.returncode == 0:
        return True, f"Uninstalled {cli['display_name']}"
    return False, f"npm uninstall failed:\n{result.stderr}"


def _npm_update(cli):
    npm = _find_npm()
    if npm is None:
        return False, "npm is not installed."
    result = subprocess.run(
        [npm, "install", "-g", cli["npm_package"] + "@latest"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, f"Updated {cli['display_name']} to latest"
    return False, f"Update failed:\n{result.stderr}"
