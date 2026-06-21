# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackend:
    def test_default_base_url(self):
        from cli_anything.obsidian.utils.obsidian_backend import DEFAULT_BASE_URL

        assert DEFAULT_BASE_URL == "https://localhost:27124"

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.get")
    def test_is_available_true(self, mock_get):
        from cli_anything.obsidian.utils.obsidian_backend import is_available

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        assert is_available("test-key") is True
        mock_get.assert_called_once_with(
            "https://localhost:27124/",
            headers={"Authorization": "Bearer test-key"},
            timeout=5,
            verify=False,
        )

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.get")
    def test_is_available_false(self, mock_get):
        from cli_anything.obsidian.utils.obsidian_backend import is_available
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()
        assert is_available("test-key") is False

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.get")
    def test_api_get_connection_error(self, mock_get):
        from cli_anything.obsidian.utils.obsidian_backend import api_get
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(RuntimeError, match="Cannot connect to Obsidian"):
            api_get("https://localhost:27124", "/", "test-key")

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.post")
    def test_api_post_connection_error(self, mock_post):
        from cli_anything.obsidian.utils.obsidian_backend import api_post
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(RuntimeError, match="Cannot connect to Obsidian"):
            api_post(
                "https://localhost:27124",
                "/search/",
                "test-key",
                data={"query": "test"},
            )

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.delete")
    def test_api_delete_connection_error(self, mock_delete):
        from cli_anything.obsidian.utils.obsidian_backend import api_delete
        import requests

        mock_delete.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(RuntimeError, match="Cannot connect to Obsidian"):
            api_delete("https://localhost:27124", "/vault/test.md", "test-key")

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.get")
    def test_api_get_json_response(self, mock_get):
        from cli_anything.obsidian.utils.obsidian_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"files": []}'
        mock_resp.headers = {"content-type": "application/json"}
        mock_resp.json.return_value = {"files": []}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = api_get("https://localhost:27124", "/vault/", "test-key")
        assert result == {"files": []}

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.get")
    def test_api_get_text_response(self, mock_get):
        from cli_anything.obsidian.utils.obsidian_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"# My Note\nHello world"
        mock_resp.headers = {"content-type": "text/markdown"}
        mock_resp.text = "# My Note\nHello world"
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = api_get("https://localhost:27124", "/vault/test.md", "test-key")
        assert result == {"content": "# My Note\nHello world"}

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.get")
    def test_api_get_trailing_slash_stripped(self, mock_get):
        from cli_anything.obsidian.utils.obsidian_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"status": "ok"}'
        mock_resp.headers = {"content-type": "application/json"}
        mock_resp.json.return_value = {"status": "ok"}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        api_get("https://localhost:27124/", "/", "test-key")
        mock_get.assert_called_once_with(
            "https://localhost:27124/",
            headers={"Authorization": "Bearer test-key", "Accept": "application/json"},
            params=None,
            timeout=30,
            verify=False,
        )

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.get")
    def test_api_get_timeout(self, mock_get):
        from cli_anything.obsidian.utils.obsidian_backend import api_get
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(RuntimeError, match="timed out"):
            api_get("https://localhost:27124", "/", "test-key")

    @patch("cli_anything.obsidian.utils.obsidian_backend.requests.put")
    def test_api_put_text(self, mock_put):
        from cli_anything.obsidian.utils.obsidian_backend import api_put

        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_resp.raise_for_status.return_value = None
        mock_put.return_value = mock_resp
        result = api_put(
            "https://localhost:27124", "/vault/test.md", "test-key", content="# Hello"
        )
        assert result == {"status": "ok"}
