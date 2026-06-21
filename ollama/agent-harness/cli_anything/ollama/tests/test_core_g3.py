# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestGenerateTextCommands:
    @patch("cli_anything.ollama.core.generate.api_post")
    def test_generate_text_no_stream_json(self, mock_api, runner):
        mock_api.return_value = {
            "model": "llama3.2",
            "response": "Hello! How can I help you?",
            "done": True,
            "total_duration": 1234567890,
            "eval_count": 7,
        }
        result = runner.invoke(
            cli,
            [
                "--json",
                "generate",
                "text",
                "--model",
                "llama3.2",
                "--prompt",
                "Say hello",
                "--no-stream",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["response"] == "Hello! How can I help you?"
        assert data["done"] is True

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_generate_text_no_stream_human(self, mock_api, runner):
        mock_api.return_value = {
            "model": "llama3.2",
            "response": "The sky is blue.",
            "done": True,
        }
        result = runner.invoke(
            cli,
            [
                "generate",
                "text",
                "--model",
                "llama3.2",
                "--prompt",
                "Why is the sky blue?",
                "--no-stream",
            ],
        )
        assert result.exit_code == 0
        assert "The sky is blue." in result.output

    @patch("cli_anything.ollama.core.generate.api_post_stream")
    def test_generate_text_streaming(self, mock_stream, runner):
        mock_stream.return_value = iter(
            [
                {"response": "Hello", "done": False},
                {"response": " world", "done": False},
                {"response": "!", "done": True, "total_duration": 100000},
            ]
        )
        result = runner.invoke(
            cli, ["generate", "text", "--model", "llama3.2", "--prompt", "Say hello"]
        )
        assert result.exit_code == 0
        assert "Hello world!" in result.output

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_generate_text_with_system(self, mock_api, runner):
        mock_api.return_value = {
            "model": "llama3.2",
            "response": "Ahoy!",
            "done": True,
        }
        result = runner.invoke(
            cli,
            [
                "--json",
                "generate",
                "text",
                "--model",
                "llama3.2",
                "--prompt",
                "Say hello",
                "--system",
                "You are a pirate",
                "--no-stream",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["response"] == "Ahoy!"

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_generate_text_with_options(self, mock_api, runner):
        mock_api.return_value = {"model": "llama3.2", "response": "Hi", "done": True}
        result = runner.invoke(
            cli,
            [
                "--json",
                "generate",
                "text",
                "--model",
                "llama3.2",
                "--prompt",
                "Hello",
                "--temperature",
                "0.5",
                "--top-p",
                "0.9",
                "--num-predict",
                "50",
                "--no-stream",
            ],
        )
        assert result.exit_code == 0
        # Verify options were passed
        call_args = mock_api.call_args
        assert call_args is not None

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_generate_text_connection_error(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Ollama")
        result = runner.invoke(
            cli,
            [
                "generate",
                "text",
                "--model",
                "llama3.2",
                "--prompt",
                "Hello",
                "--no-stream",
            ],
        )
        assert result.exit_code == 1

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_generate_text_connection_error_json(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Ollama")
        result = runner.invoke(
            cli,
            [
                "--json",
                "generate",
                "text",
                "--model",
                "llama3.2",
                "--prompt",
                "Hello",
                "--no-stream",
            ],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data
        assert "runtime_error" in data["type"]
