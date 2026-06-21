# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestModelPullCommands:
    @patch("cli_anything.ollama.core.models.api_post")
    def test_pull_no_stream(self, mock_api, runner):
        mock_api.return_value = {"status": "success"}
        result = runner.invoke(cli, ["model", "pull", "llama3.2", "--no-stream"])
        assert result.exit_code == 0
        assert "Pulled" in result.output

    @patch("cli_anything.ollama.core.models.api_post")
    def test_pull_no_stream_json(self, mock_api, runner):
        mock_api.return_value = {"status": "success"}
        result = runner.invoke(cli, ["--json", "model", "pull", "llama3.2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"

    @patch("cli_anything.ollama.core.models.api_post_stream")
    def test_pull_streaming(self, mock_stream, runner):
        mock_stream.return_value = iter(
            [
                {"status": "pulling manifest"},
                {
                    "status": "downloading",
                    "digest": "sha256:abc123",
                    "total": 1000,
                    "completed": 500,
                },
                {
                    "status": "downloading",
                    "digest": "sha256:abc123",
                    "total": 1000,
                    "completed": 1000,
                },
                {"status": "verifying sha256 digest"},
                {"status": "writing manifest"},
                {"status": "success"},
            ]
        )
        result = runner.invoke(cli, ["model", "pull", "llama3.2"])
        assert result.exit_code == 0
        assert "Done" in result.output

    @patch("cli_anything.ollama.core.models.api_post_stream")
    def test_pull_streaming_error(self, mock_stream, runner):
        mock_stream.return_value = iter(
            [
                {"status": "downloading"},
                {"error": "disk full"},
            ]
        )
        result = runner.invoke(cli, ["model", "pull", "llama3.2"])
        assert result.exit_code == 1
        assert "Error: disk full" in result.output

    @patch("cli_anything.ollama.core.models.api_post")
    def test_pull_connection_error(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Ollama")
        result = runner.invoke(cli, ["model", "pull", "llama3.2", "--no-stream"])
        assert result.exit_code == 1


class TestModelPsCommands:
    @patch("cli_anything.ollama.core.models.api_get")
    def test_ps_with_models(self, mock_api, runner):
        mock_api.return_value = {
            "models": [
                {
                    "name": "llama3.2:latest",
                    "size": 3825819519,
                    "size_vram": 3825819519,
                    "expires_at": "2024-06-04T14:38:31.83753-07:00",
                }
            ]
        }
        result = runner.invoke(cli, ["model", "ps"])
        assert result.exit_code == 0
        assert "llama3.2:latest" in result.output

    @patch("cli_anything.ollama.core.models.api_get")
    def test_ps_with_models_json(self, mock_api, runner):
        mock_api.return_value = {
            "models": [
                {
                    "name": "llama3.2:latest",
                    "size": 3825819519,
                    "size_vram": 3825819519,
                }
            ]
        }
        result = runner.invoke(cli, ["--json", "model", "ps"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["models"]) == 1
        assert data["models"][0]["name"] == "llama3.2:latest"


class TestModelShowCommands:
    @patch("cli_anything.ollama.core.models.api_post")
    def test_show_human_output(self, mock_api, runner):
        mock_api.return_value = {
            "modelfile": "FROM llama3.2\nPARAMETER temperature 0.7",
            "parameters": "temperature 0.7\ntop_p 0.9",
            "template": "{{ .Prompt }}",
            "details": {
                "parent_model": "",
                "format": "gguf",
                "family": "llama",
                "parameter_size": "3.2B",
                "quantization_level": "Q4_0",
            },
        }
        result = runner.invoke(cli, ["model", "show", "llama3.2"])
        assert result.exit_code == 0
        assert "llama3.2" in result.output

    @patch("cli_anything.ollama.core.models.api_post")
    def test_show_json_output(self, mock_api, runner):
        mock_api.return_value = {
            "modelfile": "FROM llama3.2",
            "details": {"family": "llama", "parameter_size": "3.2B"},
        }
        result = runner.invoke(cli, ["--json", "model", "show", "llama3.2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["details"]["family"] == "llama"

    @patch("cli_anything.ollama.core.models.api_post")
    def test_show_nonexistent_model(self, mock_api, runner):
        mock_api.side_effect = RuntimeError(
            "Ollama API error 404 on POST /api/show: model not found"
        )
        result = runner.invoke(cli, ["model", "show", "nonexistent"])
        assert result.exit_code == 1
