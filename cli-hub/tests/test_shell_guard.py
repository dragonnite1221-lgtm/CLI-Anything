"""Tests for the shell-install consent gate (code review H1).

Registry entries can ship ``curl … | bash`` commands; these run remote code, so
`_run_command` must not execute a shell-operator command without consent.
"""

from unittest.mock import patch

from cli_hub._shell_guard import confirm_shell_command, has_shell_operator
from cli_hub.installer import _run_command


class TestHasShellOperator:
    def test_pipe(self):
        assert has_shell_operator("curl -s https://x/cli | bash") is True

    def test_and(self):
        assert has_shell_operator("curl -O x && bash x") is True

    def test_redirect(self):
        assert has_shell_operator("echo x > /tmp/y") is True

    def test_plain_command(self):
        assert has_shell_operator("pip install some-package") is False

    def test_brew(self):
        assert has_shell_operator("brew install --cask 1password-cli") is False


class TestConfirmShellCommand:
    def test_env_opt_in_allows(self, monkeypatch):
        monkeypatch.setenv("CLI_HUB_ALLOW_SHELL_INSTALL", "1")
        assert confirm_shell_command("curl x | bash") is True

    def test_non_interactive_without_opt_in_refuses(self, monkeypatch):
        monkeypatch.delenv("CLI_HUB_ALLOW_SHELL_INSTALL", raising=False)
        # pytest runs with a non-tty stdin, so this is refused without input().
        assert confirm_shell_command("curl x | bash") is False

    def test_interactive_yes_allows(self, monkeypatch):
        monkeypatch.delenv("CLI_HUB_ALLOW_SHELL_INSTALL", raising=False)
        monkeypatch.setattr("cli_hub._shell_guard.sys.stdin.isatty", lambda: True)
        monkeypatch.setattr("builtins.input", lambda: "y")
        assert confirm_shell_command("curl x | bash") is True

    def test_interactive_no_refuses(self, monkeypatch):
        monkeypatch.delenv("CLI_HUB_ALLOW_SHELL_INSTALL", raising=False)
        monkeypatch.setattr("cli_hub._shell_guard.sys.stdin.isatty", lambda: True)
        monkeypatch.setattr("builtins.input", lambda: "n")
        assert confirm_shell_command("curl x | bash") is False


class TestRunCommandGate:
    def test_shell_install_refused_without_consent(self, monkeypatch):
        monkeypatch.delenv("CLI_HUB_ALLOW_SHELL_INSTALL", raising=False)
        with patch("cli_hub.installer.subprocess.run") as mock_run:
            result = _run_command("curl -s https://jimeng.jianying.com/cli | bash")
        mock_run.assert_not_called()
        assert result.returncode == 126

    def test_plain_command_runs_without_prompt(self, monkeypatch):
        monkeypatch.delenv("CLI_HUB_ALLOW_SHELL_INSTALL", raising=False)
        with patch("cli_hub.installer.subprocess.run") as mock_run:
            mock_run.return_value = None
            _run_command("pip install some-package")
        mock_run.assert_called_once()
