# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIParsing:
    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Ollama CLI" in result.output

    def test_model_help(self, runner):
        result = runner.invoke(cli, ["model", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "show" in result.output
        assert "pull" in result.output
        assert "rm" in result.output
        assert "copy" in result.output
        assert "ps" in result.output

    def test_generate_help(self, runner):
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "text" in result.output
        assert "chat" in result.output

    def test_embed_help(self, runner):
        result = runner.invoke(cli, ["embed", "--help"])
        assert result.exit_code == 0
        assert "text" in result.output

    def test_server_help(self, runner):
        result = runner.invoke(cli, ["server", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output
        assert "version" in result.output

    def test_session_help(self, runner):
        result = runner.invoke(cli, ["session", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output
        assert "history" in result.output

    def test_json_flag(self, runner):
        result = runner.invoke(cli, ["--json", "session", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "host" in data

    def test_host_flag(self, runner):
        result = runner.invoke(
            cli, ["--host", "http://example:1234", "--json", "session", "status"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["host"] == "http://example:1234"


class TestSessionState:
    def test_session_status_defaults(self, runner):
        result = runner.invoke(cli, ["--json", "session", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["chat_history_length"] == 0

    def test_session_history_empty(self, runner):
        result = runner.invoke(cli, ["--json", "session", "history"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["messages"] == []

    def test_session_history_human(self, runner):
        result = runner.invoke(cli, ["session", "history"])
        assert result.exit_code == 0
        assert "No chat history" in result.output


class TestErrorHandling:
    @patch("cli_anything.ollama.core.models.api_get")
    def test_model_list_connection_error(self, mock_api, runner):
        mock_api.side_effect = RuntimeError(
            "Cannot connect to Ollama at http://localhost:11434. "
            "Is Ollama running? Start it with: ollama serve"
        )
        result = runner.invoke(cli, ["model", "list"])
        assert result.exit_code == 1

    @patch("cli_anything.ollama.core.models.api_get")
    def test_model_list_connection_error_json(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Ollama")
        result = runner.invoke(cli, ["--json", "model", "list"])
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data

    @patch("cli_anything.ollama.core.server.api_get")
    def test_server_status_error(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Ollama")
        result = runner.invoke(cli, ["server", "status"])
        assert result.exit_code == 1

    def test_generate_chat_no_messages(self, runner):
        result = runner.invoke(cli, ["generate", "chat", "--model", "test"])
        assert result.exit_code == 1

    def test_generate_chat_bad_format(self, runner):
        result = runner.invoke(
            cli, ["generate", "chat", "--model", "test", "--message", "no-colon-here"]
        )
        assert result.exit_code == 1
