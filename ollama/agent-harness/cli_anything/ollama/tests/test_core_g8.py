# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCoreModules:
    @patch("cli_anything.ollama.core.generate.api_post")
    def test_generate_builds_correct_payload(self, mock_api):
        from cli_anything.ollama.core.generate import generate

        mock_api.return_value = {"response": "hi", "done": True}
        generate(
            "http://localhost:11434",
            "llama3.2",
            "Hello",
            system="Be helpful",
            options={"temperature": 0.5},
            stream=False,
        )
        call_data = mock_api.call_args[0][2]
        assert call_data["model"] == "llama3.2"
        assert call_data["prompt"] == "Hello"
        assert call_data["system"] == "Be helpful"
        assert call_data["options"]["temperature"] == 0.5
        assert call_data["stream"] is False

    @patch("cli_anything.ollama.core.generate.api_post")
    def test_chat_builds_correct_payload(self, mock_api):
        from cli_anything.ollama.core.generate import chat

        mock_api.return_value = {
            "message": {"role": "assistant", "content": "hi"},
            "done": True,
        }
        messages = [{"role": "user", "content": "Hello"}]
        chat(
            "http://localhost:11434",
            "llama3.2",
            messages,
            options={"temperature": 0.8},
            stream=False,
        )
        call_data = mock_api.call_args[0][2]
        assert call_data["model"] == "llama3.2"
        assert call_data["messages"] == messages
        assert call_data["options"]["temperature"] == 0.8

    @patch("cli_anything.ollama.core.embeddings.api_post")
    def test_embed_builds_correct_payload(self, mock_api):
        from cli_anything.ollama.core.embeddings import embed

        mock_api.return_value = {"embeddings": [[0.1, 0.2]]}
        embed("http://localhost:11434", "nomic-embed-text", "test input")
        call_data = mock_api.call_args[0][2]
        assert call_data["model"] == "nomic-embed-text"
        assert call_data["input"] == "test input"

    @patch("cli_anything.ollama.core.embeddings.api_post")
    def test_embed_list_input(self, mock_api):
        from cli_anything.ollama.core.embeddings import embed

        mock_api.return_value = {"embeddings": [[0.1], [0.2]]}
        embed("http://localhost:11434", "nomic-embed-text", ["hello", "world"])
        call_data = mock_api.call_args[0][2]
        assert call_data["input"] == ["hello", "world"]

    @patch("cli_anything.ollama.core.models.api_post")
    def test_copy_model_payload(self, mock_api):
        from cli_anything.ollama.core.models import copy_model

        mock_api.return_value = {"status": "ok"}
        copy_model("http://localhost:11434", "llama3.2", "my-llama")
        call_data = mock_api.call_args[0][2]
        assert call_data["source"] == "llama3.2"
        assert call_data["destination"] == "my-llama"

    @patch("cli_anything.ollama.core.models.api_delete")
    def test_delete_model_payload(self, mock_api):
        from cli_anything.ollama.core.models import delete_model

        mock_api.return_value = {"status": "ok"}
        delete_model("http://localhost:11434", "old-model")
        call_data = mock_api.call_args[0][2]
        assert call_data["name"] == "old-model"


class TestStreamToStdout:
    def test_stream_to_stdout_generate(self, capsys):
        from cli_anything.ollama.core.generate import stream_to_stdout

        chunks = iter(
            [
                {"response": "Hello", "done": False},
                {"response": " there", "done": False},
                {"response": "!", "done": True, "total_duration": 999},
            ]
        )
        final = stream_to_stdout(chunks)
        captured = capsys.readouterr()
        assert "Hello there!" in captured.out
        assert final["done"] is True
        assert final["total_duration"] == 999

    def test_stream_to_stdout_chat(self, capsys):
        from cli_anything.ollama.core.generate import stream_to_stdout

        chunks = iter(
            [
                {"message": {"role": "assistant", "content": "Yes"}, "done": False},
                {"message": {"role": "assistant", "content": "!"}, "done": True},
            ]
        )
        final = stream_to_stdout(chunks)
        captured = capsys.readouterr()
        assert "Yes!" in captured.out

    def test_stream_to_stdout_empty(self, capsys):
        from cli_anything.ollama.core.generate import stream_to_stdout

        chunks = iter([{"done": True}])
        final = stream_to_stdout(chunks)
        captured = capsys.readouterr()
        assert final["done"] is True
