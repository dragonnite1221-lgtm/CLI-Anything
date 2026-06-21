# ruff: noqa: F403, F405, E501
from .installer_base import *  # noqa: F403

# fmt: off
from .installer_p1 import _bundled_install, _generic_install, _generic_uninstall, _generic_update, _install_strategy, _load_installed, _save_installed  # noqa: E402,E501
from .installer_p2 import _bundled_uninstall, _bundled_update, _npm_install, _npm_uninstall, _npm_update, _pip_install, _pip_uninstall, _pip_update, _uv_install, _uv_uninstall, _uv_update  # noqa: E402,E501
# fmt: on


def _perform_action(cli, action):
    """Dispatch install/uninstall/update based on CLI strategy."""
    strategy = _install_strategy(cli)
    actions = {
        "pip": {
            "install": _pip_install,
            "uninstall": _pip_uninstall,
            "update": _pip_update,
        },
        "npm": {
            "install": _npm_install,
            "uninstall": _npm_uninstall,
            "update": _npm_update,
        },
        "uv": {
            "install": _uv_install,
            "uninstall": _uv_uninstall,
            "update": _uv_update,
        },
        "command": {
            "install": _generic_install,
            "uninstall": _generic_uninstall,
            "update": _generic_update,
        },
        "bundled": {
            "install": _bundled_install,
            "uninstall": _bundled_uninstall,
            "update": _bundled_update,
        },
    }
    handler = actions.get(strategy, actions["command"]).get(action)
    return strategy, handler(cli)


def _installed_entry(cli, source, strategy):
    """Return the installed.json payload for a CLI."""
    entry = {
        "version": cli["version"],
        "entry_point": cli["entry_point"],
        "source": source,
        "strategy": strategy,
    }
    if cli.get("package_manager"):
        entry["package_manager"] = cli["package_manager"]
    if cli.get("npm_package"):
        entry["npm_package"] = cli["npm_package"]
    if cli.get("install_cmd"):
        entry["install_cmd"] = cli["install_cmd"]
    if cli.get("uninstall_cmd"):
        entry["uninstall_cmd"] = cli["uninstall_cmd"]
    if cli.get("update_cmd"):
        entry["update_cmd"] = cli["update_cmd"]
    return entry


def install_cli(name):
    """Install a CLI by name. Dispatches to pip or npm based on source. Returns (success, message)."""
    cli = get_cli(name)
    if cli is None:
        return (
            False,
            f"CLI '{name}' not found in registry. Use 'cli-hub list' to see available CLIs.",
        )

    source = cli.get("_source", "harness")
    strategy, (success, msg) = _perform_action(cli, "install")

    if success:
        installed = _load_installed()
        installed[cli["name"]] = _installed_entry(cli, source, strategy)
        _save_installed(installed)

    return success, msg


def uninstall_cli(name):
    """Uninstall a CLI by name. Returns (success, message)."""
    cli = get_cli(name)
    if cli is None:
        return False, f"CLI '{name}' not found in registry."

    _, (success, msg) = _perform_action(cli, "uninstall")

    if success:
        installed = _load_installed()
        installed.pop(cli["name"], None)
        _save_installed(installed)

    return success, msg


def update_cli(name):
    """Update a CLI by reinstalling. Returns (success, message)."""
    cli = get_cli(name, force_refresh=True)
    if cli is None:
        return False, f"CLI '{name}' not found in registry."

    source = cli.get("_source", "harness")
    strategy, (success, msg) = _perform_action(cli, "update")

    if success:
        installed = _load_installed()
        installed[cli["name"]] = _installed_entry(cli, source, strategy)
        _save_installed(installed)

    return success, msg


def get_installed():
    """Return dict of installed CLIs."""
    return _load_installed()
