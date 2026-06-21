# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackendStreaming:
    @patch("cli_anything.ollama.utils.ollama_backend.requests.post")
    def test_api_post_stream_success(self, mock_post):
        from cli_anything.ollama.utils.ollama_backend import api_post_stream

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'{"response": " world", "done": true}',
        ]
        mock_post.return_value = mock_resp
        chunks = list(
            api_post_stream(
                "http://localhost:11434", "/api/generate", {"model": "test"}
            )
        )
        assert len(chunks) == 2
        assert chunks[0]["response"] == "Hello"
        assert chunks[1]["done"] is True

    @patch("cli_anything.ollama.utils.ollama_backend.requests.post")
    def test_api_post_stream_connection_error(self, mock_post):
        from cli_anything.ollama.utils.ollama_backend import api_post_stream
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(RuntimeError, match="Cannot connect to Ollama"):
            list(api_post_stream("http://localhost:11434", "/api/generate", {}))

    @patch("cli_anything.ollama.utils.ollama_backend.requests.post")
    def test_api_post_stream_skips_empty_lines(self, mock_post):
        from cli_anything.ollama.utils.ollama_backend import api_post_stream

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.iter_lines.return_value = [
            b'{"response": "Hi", "done": false}',
            b"",
            b'{"response": "!", "done": true}',
        ]
        mock_post.return_value = mock_resp
        chunks = list(api_post_stream("http://localhost:11434", "/api/generate", {}))
        assert len(chunks) == 2
