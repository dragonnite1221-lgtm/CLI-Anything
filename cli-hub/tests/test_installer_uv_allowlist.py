"""Regression tests for CLI-Anything-1: a registry entry declaring
install_strategy/package_manager "uv" must not be able to smuggle an arbitrary
interpreter command past the same allowlist that brew/pip registry commands
go through.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from cli_hub.installer import install_cli, uninstall_cli, update_cli

GENERATE_VEO_CLI = {
    "name": "generate-veo-video",
    "display_name": "Generate Veo Video",
    "version": "0.2.5",
    "description": "CLI for generating videos with Google Veo 3.1",
    "category": "ai",
    "entry_point": "generate-veo",
    "_source": "public",
    "package_manager": "uv",
    "install_cmd": "uv tool install git+https://github.com/charles-forsyth/generate-veo-video.git",
    "uninstall_cmd": "uv tool uninstall generate-veo-video",
    "update_cmd": "uv tool upgrade generate-veo-video",
}

MALICIOUS_UV_CLI = {
    **GENERATE_VEO_CLI,
    "name": "evil-uv-tool",
    "display_name": "Evil Uv Tool",
    "install_cmd": "python3 -c 'print(123)'",
    "uninstall_cmd": "python3 -c 'print(123)'",
    "update_cmd": "python3 -c 'print(123)'",
}


class TestUvStrategyCommandAllowlist:
    """Regression tests for CLI-Anything-1 (uv strategy bypassing command allowlist)."""

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_install_uv_rejects_non_uv_command(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = MALICIOUS_UV_CLI
        success, msg = install_cli("evil-uv-tool")
        mock_run.assert_not_called()
        assert not success
        assert "blocked" in msg.lower()

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_uninstall_uv_rejects_non_uv_command(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = MALICIOUS_UV_CLI
        success, msg = uninstall_cli("evil-uv-tool")
        mock_run.assert_not_called()
        assert not success
        assert "blocked" in msg.lower()

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_update_uv_rejects_non_uv_command(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = MALICIOUS_UV_CLI
        success, msg = update_cli("evil-uv-tool")
        mock_run.assert_not_called()
        assert not success
        assert "blocked" in msg.lower()

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_install_uv_still_accepts_legitimate_command(self, mock_find_uv, mock_get_cli, mock_run):
        mock_get_cli.return_value = GENERATE_VEO_CLI
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        success, msg = install_cli("generate-veo-video")
        assert success
        mock_run.assert_called_once()
        assert mock_run.call_args.args[0] == [
            "/usr/bin/uv", "tool", "install", "git+https://github.com/charles-forsyth/generate-veo-video.git"
        ]

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_install_uv_rejects_path_smuggled_binary(self, mock_find_uv, mock_get_cli, mock_run):
        """The registry command names a path, not the literal "uv"; only the
        trusted resolved executable from _find_uv() must ever be exec'd."""
        smuggled = {**GENERATE_VEO_CLI, "install_cmd": "/attacker/dir/uv tool install pkg"}
        mock_get_cli.return_value = smuggled
        success, msg = install_cli("generate-veo-video")
        mock_run.assert_not_called()
        assert not success
        assert "blocked" in msg.lower()

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    @patch("cli_hub.installer._find_uv", return_value="/usr/bin/uv")
    def test_install_strategy_uv_without_package_manager_still_works(self, mock_find_uv, mock_get_cli, mock_run):
        """CLI-Anything-1 P2: install_strategy="uv" alone (no package_manager)
        must still route through the uv allowlist, not be rejected as an
        unspecified manager."""
        entry = {**GENERATE_VEO_CLI, "package_manager": None, "install_strategy": "uv"}
        mock_get_cli.return_value = entry
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        success, msg = install_cli("generate-veo-video")
        assert success
        mock_run.assert_called_once()
