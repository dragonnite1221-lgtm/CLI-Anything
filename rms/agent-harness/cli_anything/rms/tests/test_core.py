# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBackend:
    """Tests for rms_backend module."""

    def test_get_api_token_from_env(self):
        from cli_anything.rms.utils.rms_backend import get_api_token

        with patch.dict(os.environ, {"RMS_API_TOKEN": "test-token-123"}):
            assert get_api_token() == "test-token-123"

    def test_get_api_token_cli_override(self):
        from cli_anything.rms.utils.rms_backend import get_api_token

        with patch.dict(os.environ, {"RMS_API_TOKEN": "env-token"}):
            assert get_api_token("cli-token") == "cli-token"

    def test_get_api_token_from_config(self, tmp_path):
        from cli_anything.rms.utils import rms_backend

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"api_token": "config-token"}))

        with patch.object(rms_backend, "CONFIG_FILE", config_file):
            with patch.dict(os.environ, {}, clear=True):
                # Remove RMS_API_TOKEN if present
                os.environ.pop("RMS_API_TOKEN", None)
                assert rms_backend.get_api_token() == "config-token"

    def test_require_api_token_missing(self):
        from cli_anything.rms.utils.rms_backend import _require_api_token

        with pytest.raises(RuntimeError, match="RMS API token not found"):
            _require_api_token(None)

    def test_require_api_token_present(self):
        from cli_anything.rms.utils.rms_backend import _require_api_token

        assert _require_api_token("my-token") == "my-token"

    def test_make_auth_headers(self):
        from cli_anything.rms.utils.rms_backend import _make_auth_headers

        headers = _make_auth_headers("test-token")
        assert headers == {"Authorization": "Bearer test-token"}

    @patch("cli_anything.rms.utils.rms_backend.requests")
    def test_api_get_success(self, mock_requests):
        from cli_anything.rms.utils.rms_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "success": True,
            "data": [{"id": 1, "name": "Router-1"}],
            "meta": {"total": 1},
        }
        mock_resp.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_resp

        result = api_get("/devices", token="test-token")
        assert result["success"] is True
        assert len(result["data"]) == 1

    @patch("cli_anything.rms.utils.rms_backend.requests")
    def test_api_get_with_params(self, mock_requests):
        from cli_anything.rms.utils.rms_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True, "data": []}
        mock_resp.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_resp

        api_get(
            "/devices", params={"status": "online", "limit": 10}, token="test-token"
        )
        mock_requests.get.assert_called_once()
        call_kwargs = mock_requests.get.call_args
        assert call_kwargs.kwargs["params"] == {"status": "online", "limit": 10}

    @patch("cli_anything.rms.utils.rms_backend.requests")
    def test_api_get_error(self, mock_requests):
        import requests as _requests
        from cli_anything.rms.utils.rms_backend import api_get

        # Preserve real exception classes so except clauses work
        mock_requests.RequestException = _requests.RequestException
        mock_requests.exceptions = _requests.exceptions

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = '{"success": false, "errors": [{"message": "Not found"}]}'
        mock_resp.json.return_value = {
            "success": False,
            "errors": [{"message": "Not found"}],
        }
        mock_resp.raise_for_status.side_effect = _requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_requests.get.return_value = mock_resp

        with pytest.raises(RuntimeError, match="Not found"):
            api_get("/devices/999999", token="test-token")

    @patch("cli_anything.rms.utils.rms_backend.requests")
    def test_api_get_rate_limited(self, mock_requests):
        from cli_anything.rms.utils.rms_backend import api_get

        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.headers = {"Retry-After": "60"}
        mock_resp.text = "Rate limit exceeded"
        mock_resp.raise_for_status.side_effect = Exception("429 Too Many Requests")
        mock_requests.get.return_value = mock_resp

        with pytest.raises(RuntimeError, match="[Rr]ate limit"):
            api_get("/devices", token="test-token")

    @patch("cli_anything.rms.utils.rms_backend.requests")
    def test_api_post_success(self, mock_requests):
        from cli_anything.rms.utils.rms_backend import api_post

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "success": True,
            "data": {"id": 10, "name": "New Tag"},
        }
        mock_resp.raise_for_status = MagicMock()
        mock_requests.post.return_value = mock_resp

        result = api_post("/tags", data={"name": "New Tag"}, token="test-token")
        assert result["success"] is True

    @patch("cli_anything.rms.utils.rms_backend.requests")
    def test_api_put_success(self, mock_requests):
        from cli_anything.rms.utils.rms_backend import api_put

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "success": True,
            "data": {"id": 10, "name": "Updated"},
        }
        mock_resp.raise_for_status = MagicMock()
        mock_requests.put.return_value = mock_resp

        result = api_put("/tags/10", data={"name": "Updated"}, token="test-token")
        assert result["success"] is True

    @patch("cli_anything.rms.utils.rms_backend.requests")
    def test_api_delete_success(self, mock_requests):
        from cli_anything.rms.utils.rms_backend import api_delete

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True}
        mock_resp.raise_for_status = MagicMock()
        mock_requests.delete.return_value = mock_resp

        result = api_delete("/tags/10", token="test-token")
        assert result["success"] is True

    def test_config_save_load(self, tmp_path):
        from cli_anything.rms.utils import rms_backend

        config_file = tmp_path / "config.json"
        with patch.object(rms_backend, "CONFIG_FILE", config_file):
            with patch.object(rms_backend, "CONFIG_DIR", tmp_path):
                rms_backend.save_config(
                    {"api_token": "saved-token", "default_limit": 50}
                )
                loaded = rms_backend.load_config()
                assert loaded["api_token"] == "saved-token"
                assert loaded["default_limit"] == 50
