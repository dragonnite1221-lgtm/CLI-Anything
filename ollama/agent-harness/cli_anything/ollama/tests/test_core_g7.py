# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackendHTTPErrors:
    @patch("cli_anything.ollama.utils.ollama_backend.requests.post")
    def test_api_post_http_error(self, mock_post):
        from cli_anything.ollama.utils.ollama_backend import api_post
        import requests

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "model not found"
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_resp
        with pytest.raises(RuntimeError, match="Ollama API error 404"):
            api_post("http://localhost:11434", "/api/show", {"name": "bad"})

    @patch("cli_anything.ollama.utils.ollama_backend.requests.post")
    def test_api_post_timeout(self, mock_post):
        from cli_anything.ollama.utils.ollama_backend import api_post
        import requests

        mock_post.side_effect = requests.exceptions.Timeout()
        with pytest.raises(RuntimeError, match="timed out"):
            api_post("http://localhost:11434", "/api/show", {"name": "test"})

    @patch("cli_anything.ollama.utils.ollama_backend.requests.delete")
    def test_api_delete_http_error(self, mock_delete):
        from cli_anything.ollama.utils.ollama_backend import api_delete
        import requests

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "model not found"
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_delete.return_value = mock_resp
        with pytest.raises(RuntimeError, match="Ollama API error 404"):
            api_delete("http://localhost:11434", "/api/delete", {"name": "bad"})

    @patch("cli_anything.ollama.utils.ollama_backend.requests.delete")
    def test_api_delete_timeout(self, mock_delete):
        from cli_anything.ollama.utils.ollama_backend import api_delete
        import requests

        mock_delete.side_effect = requests.exceptions.Timeout()
        with pytest.raises(RuntimeError, match="timed out"):
            api_delete("http://localhost:11434", "/api/delete", {"name": "test"})

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_api_get_http_error(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import api_get
        import requests

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "internal server error"
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_resp
        with pytest.raises(RuntimeError, match="Ollama API error 500"):
            api_get("http://localhost:11434", "/api/tags")

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_api_get_plain_text_response(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"Ollama is running"
        mock_resp.headers = {"content-type": "text/plain"}
        mock_resp.text = "Ollama is running"
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = api_get("http://localhost:11434", "/")
        assert result["message"] == "Ollama is running"

    @patch("cli_anything.ollama.utils.ollama_backend.requests.post")
    def test_api_post_204_no_content(self, mock_post):
        from cli_anything.ollama.utils.ollama_backend import api_post

        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        result = api_post(
            "http://localhost:11434", "/api/copy", {"source": "a", "destination": "b"}
        )
        assert result == {"status": "ok"}

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_is_available_timeout(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import is_available
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()
        assert is_available() is False
