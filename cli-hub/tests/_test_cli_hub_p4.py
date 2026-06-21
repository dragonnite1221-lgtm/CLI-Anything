# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


class TestInstaller:
    """Tests for installer.py — install, uninstall, tracking."""

    def test_load_installed_empty(self, tmp_path):
        with patch("cli_hub.installer.INSTALLED_FILE", tmp_path / "installed.json"):
            assert _load_installed() == {}

    def test_save_and_load_installed(self, tmp_path):
        installed_file = tmp_path / "installed.json"
        with patch("cli_hub.installer.INSTALLED_FILE", installed_file):
            _save_installed({"gimp": {"version": "1.0.0"}})
            data = _load_installed()
            assert data["gimp"]["version"] == "1.0.0"

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_success(self, mock_get_cli, mock_run):
        mock_get_cli.return_value = SAMPLE_REGISTRY["clis"][0]
        mock_run.return_value = MagicMock(returncode=0)

        success, msg = install_cli("gimp")
        assert success
        assert "GIMP" in msg

    @patch("cli_hub.installer.get_cli")
    def test_install_not_found(self, mock_get_cli):
        mock_get_cli.return_value = None
        success, msg = install_cli("nonexistent")
        assert not success
        assert "not found" in msg

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_pip_failure(self, mock_get_cli, mock_run):
        mock_get_cli.return_value = SAMPLE_REGISTRY["clis"][0]
        mock_run.return_value = MagicMock(returncode=1, stderr="some error")

        success, msg = install_cli("gimp")
        assert not success
        assert "failed" in msg

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_uninstall_success(self, mock_get_cli, mock_run):
        mock_get_cli.return_value = SAMPLE_REGISTRY["clis"][0]
        mock_run.return_value = MagicMock(returncode=0)

        success, msg = uninstall_cli("gimp")
        assert success
        assert "GIMP" in msg

    @patch("cli_hub.installer.subprocess.run")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_command_strategy_success(self, mock_get_cli, mock_run):
        mock_get_cli.return_value = {
            "name": "onepassword-cli",
            "display_name": "1Password CLI",
            "version": "latest",
            "description": "Secrets automation",
            "entry_point": "op",
            "_source": "public",
            "install_strategy": "command",
            "package_manager": "brew",
            "install_cmd": "brew install --cask 1password-cli",
        }
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")

        success, msg = install_cli("onepassword-cli")
        assert success
        assert "1Password CLI" in msg

    @patch("cli_hub.installer.subprocess.run", side_effect=FileNotFoundError(2, "No such file or directory", "brew"))
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_command_strategy_missing_executable(self, mock_get_cli, mock_run):
        mock_get_cli.return_value = {
            "name": "onepassword-cli",
            "display_name": "1Password CLI",
            "version": "latest",
            "description": "Secrets automation",
            "entry_point": "op",
            "_source": "public",
            "install_strategy": "command",
            "package_manager": "brew",
            "install_cmd": "brew install --cask 1password-cli",
        }

        success, msg = install_cli("onepassword-cli")
        assert not success
        assert "Command not found: brew" in msg

    @patch("cli_hub.installer.shutil.which", return_value="/usr/local/bin/obsidian")
    @patch("cli_hub.installer.get_cli")
    @patch("cli_hub.installer.INSTALLED_FILE", Path(tempfile.mktemp()))
    def test_install_bundled_strategy_success_when_detected(self, mock_get_cli, mock_which):
        mock_get_cli.return_value = {
            "name": "obsidian-cli",
            "display_name": "Obsidian CLI",
            "version": "bundled",
            "description": "Bundled inside Obsidian",
            "entry_point": "obsidian",
            "_source": "public",
            "install_strategy": "bundled",
            "package_manager": "bundled",
        }

        success, msg = install_cli("obsidian-cli")
        assert success
        assert "already available" in msg
