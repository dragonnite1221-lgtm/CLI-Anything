# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLI:
    """Click CliRunner tests for CLI commands."""

    def setup_method(self):
        from click.testing import CliRunner

        self.runner = CliRunner()

    def test_root_help(self):
        from cli_anything.rms.rms_cli import cli

        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Teltonika RMS CLI" in result.output
        assert "devices" in result.output
        assert "alerts" in result.output

    def test_devices_help(self):
        from cli_anything.rms.rms_cli import cli

        result = self.runner.invoke(cli, ["devices", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "get" in result.output

    def test_auth_help(self):
        from cli_anything.rms.rms_cli import cli

        result = self.runner.invoke(cli, ["auth", "--help"])
        assert result.exit_code == 0
        assert "test" in result.output
        assert "status" in result.output

    def test_devices_list_json_no_token(self):
        from cli_anything.rms.rms_cli import cli

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RMS_API_TOKEN", None)
            result = self.runner.invoke(cli, ["--json", "devices", "list"])
        assert "error" in result.output.lower() or result.exit_code != 0

    @patch("cli_anything.rms.core.devices.api_get")
    def test_devices_list_json(self, mock_api):
        from cli_anything.rms.rms_cli import cli

        mock_api.return_value = {
            "success": True,
            "data": [{"id": 1, "name": "Router1", "serial": "ABC"}],
        }
        with patch.dict(os.environ, {"RMS_API_TOKEN": "test-token"}):
            result = self.runner.invoke(cli, ["--json", "devices", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Router1"

    @patch("cli_anything.rms.core.devices.api_get")
    def test_devices_get(self, mock_api):
        from cli_anything.rms.rms_cli import cli

        mock_api.return_value = {"success": True, "data": {"id": 42, "name": "Gateway"}}
        with patch.dict(os.environ, {"RMS_API_TOKEN": "test-token"}):
            result = self.runner.invoke(cli, ["--json", "devices", "get", "42"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["id"] == 42
        assert data["data"]["name"] == "Gateway"

    @patch("cli_anything.rms.utils.rms_backend.api_get")
    def test_auth_test(self, mock_api):
        from cli_anything.rms.rms_cli import cli

        mock_api.return_value = {"success": True, "data": []}
        with patch.dict(os.environ, {"RMS_API_TOKEN": "test-token"}):
            result = self.runner.invoke(cli, ["auth", "test"])
        assert result.exit_code == 0
        assert "passed" in result.output.lower() or "ok" in result.output.lower()

    def test_passwords_update_no_password(self):
        from cli_anything.rms.rms_cli import cli

        with patch.dict(os.environ, {"RMS_API_TOKEN": "test-token"}):
            result = self.runner.invoke(cli, ["passwords", "update", "123"])
        assert result.exit_code != 0 or "error" in result.output.lower()
