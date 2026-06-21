# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestModelCommands:
    @patch("cli_anything.ollama.core.models.api_get")
    def test_model_list_empty(self, mock_api, runner):
        mock_api.return_value = {"models": []}
        result = runner.invoke(cli, ["model", "list"])
        assert result.exit_code == 0
        assert "No models" in result.output

    @patch("cli_anything.ollama.core.models.api_get")
    def test_model_list_json(self, mock_api, runner):
        mock_api.return_value = {"models": [{"name": "llama3.2", "size": 2000000000}]}
        result = runner.invoke(cli, ["--json", "model", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["models"]) == 1

    @patch("cli_anything.ollama.core.models.api_get")
    def test_model_list_formatted(self, mock_api, runner):
        mock_api.return_value = {
            "models": [
                {
                    "name": "llama3.2:latest",
                    "size": 2000000000,
                    "modified_at": "2024-01-01T00:00:00Z",
                }
            ]
        }
        result = runner.invoke(cli, ["model", "list"])
        assert result.exit_code == 0
        assert "llama3.2:latest" in result.output

    @patch("cli_anything.ollama.core.models.api_post")
    def test_model_show(self, mock_api, runner):
        mock_api.return_value = {
            "modelfile": "FROM llama3.2",
            "parameters": "temperature 0.7",
        }
        result = runner.invoke(cli, ["--json", "model", "show", "llama3.2"])
        assert result.exit_code == 0

    @patch("cli_anything.ollama.core.models.api_delete")
    def test_model_rm(self, mock_api, runner):
        mock_api.return_value = {"status": "ok"}
        result = runner.invoke(cli, ["model", "rm", "test-model"])
        assert result.exit_code == 0
        assert "Deleted" in result.output

    @patch("cli_anything.ollama.core.models.api_post")
    def test_model_copy(self, mock_api, runner):
        mock_api.return_value = {"status": "ok"}
        result = runner.invoke(cli, ["model", "copy", "src", "dst"])
        assert result.exit_code == 0
        assert "Copied" in result.output

    @patch("cli_anything.ollama.core.models.api_get")
    def test_model_ps_empty(self, mock_api, runner):
        mock_api.return_value = {"models": []}
        result = runner.invoke(cli, ["model", "ps"])
        assert result.exit_code == 0
        assert "No models" in result.output


class TestServerCommands:
    @patch("cli_anything.ollama.core.server.api_get")
    def test_server_status(self, mock_api, runner):
        mock_api.return_value = {"status": "ok", "message": "Ollama is running"}
        result = runner.invoke(cli, ["server", "status"])
        assert result.exit_code == 0

    @patch("cli_anything.ollama.core.server.api_get")
    def test_server_version(self, mock_api, runner):
        mock_api.return_value = {"version": "0.1.30"}
        result = runner.invoke(cli, ["--json", "server", "version"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["version"] == "0.1.30"


class TestEmbedCommands:
    @patch("cli_anything.ollama.core.embeddings.api_post")
    def test_embed_text_json(self, mock_api, runner):
        mock_api.return_value = {"embeddings": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]]}
        result = runner.invoke(
            cli,
            [
                "--json",
                "embed",
                "text",
                "--model",
                "nomic-embed-text",
                "--input",
                "Hello world",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "embeddings" in data

    @patch("cli_anything.ollama.core.embeddings.api_post")
    def test_embed_text_multiple_inputs_json(self, mock_api, runner):
        mock_api.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
        result = runner.invoke(
            cli,
            [
                "--json",
                "embed",
                "text",
                "--model",
                "nomic-embed-text",
                "--input",
                "Hello",
                "--input",
                "World",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["embeddings"]) == 2
        call_data = mock_api.call_args[0][2]
        assert call_data["input"] == ["Hello", "World"]

    @patch("cli_anything.ollama.core.embeddings.api_post")
    def test_embed_text_human(self, mock_api, runner):
        mock_api.return_value = {"embeddings": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]]}
        result = runner.invoke(
            cli, ["embed", "text", "--model", "nomic-embed-text", "--input", "Hello"]
        )
        assert result.exit_code == 0
        assert "Dimensions: 6" in result.output

    @patch("cli_anything.ollama.core.embeddings.api_post")
    def test_embed_text_preview_values(self, mock_api, runner):
        mock_api.return_value = {
            "embeddings": [[0.123456, 0.234567, 0.345678, 0.456789, 0.567890, 0.6]]
        }
        result = runner.invoke(
            cli, ["embed", "text", "--model", "nomic-embed-text", "--input", "Hello"]
        )
        assert result.exit_code == 0
        assert "Preview:" in result.output
        assert "0.123456" in result.output

    @patch("cli_anything.ollama.core.embeddings.api_post")
    def test_embed_text_empty_embeddings(self, mock_api, runner):
        mock_api.return_value = {"embeddings": []}
        result = runner.invoke(
            cli, ["embed", "text", "--model", "nomic-embed-text", "--input", "Hello"]
        )
        assert result.exit_code == 0
