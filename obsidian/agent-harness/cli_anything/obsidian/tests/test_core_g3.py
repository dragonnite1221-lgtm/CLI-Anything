# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestErrorHandling:
    @patch("cli_anything.obsidian.core.server.api_get")
    def test_server_status_error(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Obsidian")
        result = runner.invoke(cli, ["--api-key", "k", "server", "status"])
        assert result.exit_code == 1

    @patch("cli_anything.obsidian.core.server.api_get")
    def test_server_status_error_json(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Obsidian")
        result = runner.invoke(cli, ["--json", "--api-key", "k", "server", "status"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key(self, runner):
        result = runner.invoke(cli, ["server", "status"], env={"OBSIDIAN_API_KEY": ""})
        assert result.exit_code == 1

    @patch("cli_anything.obsidian.core.vault.api_get")
    def test_vault_list_error_json(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Obsidian")
        result = runner.invoke(cli, ["--json", "--api-key", "k", "vault", "list"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data
