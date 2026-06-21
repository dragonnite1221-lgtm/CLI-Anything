# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestGenerateChatCommands:
    @patch("cli_anything.ollama.core.generate.api_post")
    def test_chat_no_stream_json(self, mock_api, runner):
        mock_api.return_value = {
            "model": "llama3.2",
            "message": {"role": "assistant", "content": "Hello! How can I help?"},
            "done": True,
            "total_duration": 1234567890,
        }
        result = runner.invoke(
            cli,
            [
                "--json",
                "generate",
                "chat",
                "--model",
                "llama3.2",
                "--message",
                "user:Hi there",
                "--no-stream",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["message"]["role"] == "assistant"
        assert "Hello" in data["message"]["content"]

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_chat_multi_message(self, mock_api, runner):
        mock_api.return_value = {
            "model": "llama3.2",
            "message": {"role": "assistant", "content": "Python is great!"},
            "done": True,
        }
        result = runner.invoke(
            cli,
            [
                "--json",
                "generate",
                "chat",
                "--model",
                "llama3.2",
                "--message",
                "user:What is Python?",
                "--message",
                "assistant:It's a programming language",
                "--message",
                "user:Tell me more",
                "--no-stream",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["message"]["content"] == "Python is great!"

    @patch("cli_anything.ollama.core.generate.api_post_stream")
    def test_chat_streaming(self, mock_stream, runner):
        mock_stream.return_value = iter(
            [
                {"message": {"role": "assistant", "content": "I'm"}, "done": False},
                {"message": {"role": "assistant", "content": " doing"}, "done": False},
                {"message": {"role": "assistant", "content": " well!"}, "done": True},
            ]
        )
        result = runner.invoke(
            cli,
            [
                "generate",
                "chat",
                "--model",
                "llama3.2",
                "--message",
                "user:How are you?",
            ],
        )
        assert result.exit_code == 0
        assert "I'm doing well!" in result.output

    @patch("cli_anything.ollama.core.generate.api_post_stream")
    def test_chat_streaming_error(self, mock_stream, runner):
        mock_stream.return_value = iter(
            [
                {"message": {"role": "assistant", "content": "partial"}, "done": False},
                {"error": "stream failed"},
            ]
        )
        result = runner.invoke(
            cli, ["generate", "chat", "--model", "llama3.2", "--message", "user:Hello"]
        )
        assert result.exit_code == 1
        assert "Error: stream failed" in result.output

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_chat_from_file(self, mock_api, runner, tmp_path):
        messages_file = tmp_path / "messages.json"
        messages_file.write_text(
            json.dumps(
                [
                    {"role": "user", "content": "What is 2+2?"},
                ]
            )
        )
        mock_api.return_value = {
            "model": "llama3.2",
            "message": {"role": "assistant", "content": "4"},
            "done": True,
        }
        result = runner.invoke(
            cli,
            [
                "--json",
                "generate",
                "chat",
                "--model",
                "llama3.2",
                "--file",
                str(messages_file),
                "--no-stream",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["message"]["content"] == "4"

    def test_chat_missing_model(self, runner):
        result = runner.invoke(cli, ["generate", "chat", "--message", "user:Hello"])
        assert result.exit_code != 0

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_chat_connection_error(self, mock_api, runner):
        mock_api.side_effect = RuntimeError("Cannot connect to Ollama")
        result = runner.invoke(
            cli,
            [
                "generate",
                "chat",
                "--model",
                "llama3.2",
                "--message",
                "user:Hello",
                "--no-stream",
            ],
        )
        assert result.exit_code == 1
