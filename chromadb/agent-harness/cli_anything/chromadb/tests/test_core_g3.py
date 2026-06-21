# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIParsing:
    """Test Click CLI argument parsing and output formatting."""

    @pytest.fixture
    def runner(self):
        from click.testing import CliRunner

        return CliRunner()

    @pytest.fixture
    def cli(self):
        from cli_anything.chromadb.chromadb_cli import cli

        return cli

    def test_help_flag(self, runner, cli):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "ChromaDB" in result.output or "chromadb" in result.output.lower()

    def test_server_help(self, runner, cli):
        result = runner.invoke(cli, ["server", "--help"])
        assert result.exit_code == 0
        assert "heartbeat" in result.output
        assert "version" in result.output

    def test_collection_help(self, runner, cli):
        result = runner.invoke(cli, ["collection", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "create" in result.output
        assert "delete" in result.output
        assert "info" in result.output

    def test_document_help(self, runner, cli):
        result = runner.invoke(cli, ["document", "--help"])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "get" in result.output
        assert "delete" in result.output
        assert "count" in result.output

    def test_query_help(self, runner, cli):
        result = runner.invoke(cli, ["query", "--help"])
        assert result.exit_code == 0
        assert "search" in result.output

    @patch("cli_anything.chromadb.utils.chromadb_backend.ChromaDBBackend.heartbeat")
    def test_json_output_heartbeat(self, mock_hb, runner, cli):
        mock_hb.return_value = {"nanosecond_heartbeat": 9999}
        result = runner.invoke(cli, ["--json", "server", "heartbeat"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "nanosecond_heartbeat" in data

    @patch("cli_anything.chromadb.utils.chromadb_backend.ChromaDBBackend.version")
    def test_json_output_version(self, mock_ver, runner, cli):
        mock_ver.return_value = "0.6.0"
        result = runner.invoke(cli, ["--json", "server", "version"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["version"] == "0.6.0"

    @patch(
        "cli_anything.chromadb.utils.chromadb_backend.ChromaDBBackend.list_collections"
    )
    def test_json_output_collection_list(self, mock_list, runner, cli):
        mock_list.return_value = [{"name": "test_col", "id": "abc-123", "metadata": {}}]
        result = runner.invoke(cli, ["--json", "collection", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["name"] == "test_col"

    @patch("cli_anything.chromadb.utils.chromadb_backend.ChromaDBBackend.heartbeat")
    def test_human_output_heartbeat(self, mock_hb, runner, cli):
        mock_hb.return_value = {"nanosecond_heartbeat": 9999}
        result = runner.invoke(cli, ["server", "heartbeat"])
        assert result.exit_code == 0
        # Human mode should not be valid JSON
        assert "alive" in result.output.lower() or "heartbeat" in result.output.lower()

    @patch("cli_anything.chromadb.utils.chromadb_backend.ChromaDBBackend.heartbeat")
    def test_server_error_json_output(self, mock_hb, runner, cli):
        import requests

        mock_hb.side_effect = requests.ConnectionError("Connection refused")
        result = runner.invoke(cli, ["--json", "server", "heartbeat"])
        # Should exit with error
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert "error" in data

    def test_custom_host_flag(self, runner, cli):
        """Verify --host flag is accepted (even if connection fails)."""
        result = runner.invoke(cli, ["--host", "http://fake:9999", "server", "--help"])
        assert result.exit_code == 0
