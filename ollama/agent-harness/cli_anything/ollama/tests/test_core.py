# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackend:
    def test_default_base_url(self):
        assert DEFAULT_BASE_URL == "http://localhost:11434"

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_is_available_true(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import is_available

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        assert is_available() is True
        mock_get.assert_called_once_with("http://localhost:11434/", timeout=5)

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_is_available_false(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import is_available
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()
        assert is_available() is False

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_api_get_connection_error(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import api_get
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(RuntimeError, match="Cannot connect to Ollama"):
            api_get("http://localhost:11434", "/api/tags")

    @patch("cli_anything.ollama.utils.ollama_backend.requests.post")
    def test_api_post_connection_error(self, mock_post):
        from cli_anything.ollama.utils.ollama_backend import api_post
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(RuntimeError, match="Cannot connect to Ollama"):
            api_post("http://localhost:11434", "/api/show", {"name": "test"})

    @patch("cli_anything.ollama.utils.ollama_backend.requests.delete")
    def test_api_delete_connection_error(self, mock_delete):
        from cli_anything.ollama.utils.ollama_backend import api_delete
        import requests

        mock_delete.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(RuntimeError, match="Cannot connect to Ollama"):
            api_delete("http://localhost:11434", "/api/delete", {"name": "test"})

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_api_get_success(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"models": []}'
        mock_resp.headers = {"content-type": "application/json"}
        mock_resp.json.return_value = {"models": []}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = api_get("http://localhost:11434", "/api/tags")
        assert result == {"models": []}

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_api_get_trailing_slash_stripped(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"models": []}'
        mock_resp.headers = {"content-type": "application/json"}
        mock_resp.json.return_value = {"models": []}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        api_get("http://localhost:11434/", "/api/tags")
        mock_get.assert_called_once_with(
            "http://localhost:11434/api/tags", params=None, timeout=30
        )

    @patch("cli_anything.ollama.utils.ollama_backend.requests.get")
    def test_api_get_timeout(self, mock_get):
        from cli_anything.ollama.utils.ollama_backend import api_get
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(RuntimeError, match="timed out"):
            api_get("http://localhost:11434", "/api/tags")


class TestFormatSize:
    def test_zero(self):
        assert _format_size(0) == "0 B"

    def test_bytes(self):
        assert _format_size(512) == "512.0 B"

    def test_kilobytes(self):
        assert _format_size(2048) == "2.0 KB"

    def test_megabytes(self):
        result = _format_size(5 * 1024 * 1024)
        assert "MB" in result

    def test_gigabytes(self):
        result = _format_size(3 * 1024 * 1024 * 1024)
        assert "GB" in result
