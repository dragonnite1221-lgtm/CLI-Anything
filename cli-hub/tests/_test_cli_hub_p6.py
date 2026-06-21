# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


class TestScriptStrategy:
    """Tests for script/pipe-command installs (e.g. jimeng curl | bash)."""

    # ── _install_strategy routing ──────────────────────────────────────

    def test_strategy_detected_as_command(self):
        """install_strategy field takes priority — jimeng routes to 'command'."""
        assert _install_strategy(JIMENG_CLI) == "command"

    def test_strategy_script_package_manager_without_field_falls_back_to_command(self):
        """Without install_strategy field, script package_manager still routes to 'command'."""
        cli = {**JIMENG_CLI}
        del cli["install_strategy"]
        assert _install_strategy(cli) == "command"

    # ── _run_command shell detection ───────────────────────────────────

    @patch("cli_hub.installer.subprocess.run")
    def test_run_command_uses_shell_true_for_pipe(self, mock_run):
        """Pipe character triggers shell=True so bash can interpret it."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        _run_command("curl -s https://jimeng.jianying.com/cli | bash")
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs.get("shell") is True
        # cmd passed as a single string, not a list
        args = mock_run.call_args[0][0]
        assert isinstance(args, str)
        assert "| bash" in args

    @patch("cli_hub.installer.subprocess.run")
    def test_run_command_uses_shell_false_for_simple_command(self, mock_run):
        """Simple commands (no shell operators) must NOT use shell=True."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        _run_command("brew install --cask 1password-cli")
        _, kwargs = mock_run.call_args
        assert kwargs.get("shell") is False or kwargs.get("shell") is None

    @patch("cli_hub.installer.subprocess.run")
    def test_run_command_uses_shell_true_for_and_operator(self, mock_run):
        """&& operator also triggers shell=True."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        _run_command("curl -O https://example.com/install.sh && bash install.sh")
        _, kwargs = mock_run.call_args
        assert kwargs.get("shell") is True

    # ── Full install flow ──────────────────────────────────────────────

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_jimeng_success(self, mock_get_cli, mock_run):
        """install_cli('jimeng') succeeds and invokes the pipe command via shell."""
        mock_get_cli.return_value = JIMENG_CLI
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        success, msg = install_cli("jimeng")

        assert success, f"Expected success but got: {msg}"
        assert "Jimeng" in msg

        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs.get("shell") is True
        assert "| bash" in mock_run.call_args[0][0]

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_jimeng_failure_propagated(self, mock_get_cli, mock_run):
        """A non-zero exit from the curl|bash script surfaces as failure."""
        mock_get_cli.return_value = JIMENG_CLI
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="curl: (6) Could not resolve host"
        )

        success, msg = install_cli("jimeng")

        assert not success
        assert "failed" in msg.lower()

    @patch("cli_hub.installer.get_cli")
    def test_uninstall_jimeng_no_cmd_returns_graceful_message(self, mock_get_cli):
        """Uninstalling jimeng (no uninstall_cmd defined) returns a non-crash message."""
        mock_get_cli.return_value = JIMENG_CLI  # no uninstall_cmd key

        success, msg = uninstall_cli("jimeng")

        assert not success
        # Should mention the CLI name or explain no command available — never crash
        assert msg

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_jimeng_recorded_in_installed_json(self, mock_get_cli, mock_run):
        """After a successful install, jimeng appears in installed.json."""
        installed_file = Path(tempfile.mktemp())
        mock_get_cli.return_value = JIMENG_CLI
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("cli_hub.installer.INSTALLED_FILE", installed_file):
            success, _ = install_cli("jimeng")
            assert success
            data = json.loads(installed_file.read_text())
            assert "jimeng" in data
            assert data["jimeng"]["strategy"] == "command"
            assert data["jimeng"]["package_manager"] == "script"
