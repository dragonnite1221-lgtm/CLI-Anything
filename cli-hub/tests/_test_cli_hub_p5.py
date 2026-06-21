# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


class TestUvStrategy:
    """Tests for uv-managed public CLI installs (e.g. generate-veo-video)."""

    def test_strategy_detected_as_uv(self):
        assert _install_strategy(GENERATE_VEO_CLI) == "uv"

    def test_strategy_uv_not_overridden_by_install_strategy_field(self):
        """If install_strategy is explicitly set it takes priority over package_manager."""
        cli = {**GENERATE_VEO_CLI, "install_strategy": "command"}
        assert _install_strategy(cli) == "command"

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_install_uv_success(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = GENERATE_VEO_CLI
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        success, msg = install_cli("generate-veo-video")
        assert success
        assert "Generate Veo Video" in msg

    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer._find_uv", return_value=None)
    def test_install_uv_missing_shows_hint(self, mock_find_uv, mock_get_cli):
        mock_get_cli.return_value = GENERATE_VEO_CLI
        success, msg = install_cli("generate-veo-video")
        assert not success
        assert "uv is not installed" in msg
        assert "astral.sh/uv" in msg
        assert "brew install uv" in msg

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_uninstall_uv_success(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = GENERATE_VEO_CLI
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        success, msg = uninstall_cli("generate-veo-video")
        assert success
        assert "Generate Veo Video" in msg

    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer._find_uv", return_value=None)
    def test_uninstall_uv_missing_shows_hint(self, mock_find_uv, mock_get_cli):
        mock_get_cli.return_value = GENERATE_VEO_CLI
        success, msg = uninstall_cli("generate-veo-video")
        assert not success
        assert "uv is not installed" in msg

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_update_uv_success(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = GENERATE_VEO_CLI
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        from cli_hub.installer import update_cli
        success, msg = update_cli("generate-veo-video")
        assert success
        assert "Generate Veo Video" in msg

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_install_uv_failure_propagated(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = GENERATE_VEO_CLI
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error: package not found")
        success, msg = install_cli("generate-veo-video")
        assert not success
        assert "failed" in msg.lower()
