# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestHandleResponse:
    """Direct tests for _handle_response edge cases."""

    def test_success_json(self):
        from cli_anything.rms.utils.rms_backend import _handle_response

        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"success": True, "data": [1, 2, 3]}
        result = _handle_response(resp)
        assert result == {"success": True, "data": [1, 2, 3]}

    def test_success_non_json(self):
        from cli_anything.rms.utils.rms_backend import _handle_response

        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.side_effect = ValueError("No JSON")
        resp.text = "plain text body"
        result = _handle_response(resp)
        assert result == {"success": True, "data": "plain text body"}

    def test_error_with_messages(self):
        import requests as _requests
        from cli_anything.rms.utils.rms_backend import _handle_response

        resp = MagicMock()
        resp.status_code = 400
        resp.raise_for_status.side_effect = _requests.exceptions.HTTPError("400")
        resp.json.return_value = {
            "errors": [{"message": "Invalid field"}, {"message": "Missing param"}]
        }
        with pytest.raises(RuntimeError, match="Invalid field"):
            _handle_response(resp)

    def test_error_plain_text(self):
        import requests as _requests
        from cli_anything.rms.utils.rms_backend import _handle_response

        resp = MagicMock()
        resp.status_code = 500
        resp.raise_for_status.side_effect = _requests.exceptions.HTTPError("500")
        resp.json.side_effect = ValueError("No JSON")
        resp.text = "Internal Server Error"
        with pytest.raises(RuntimeError, match="Internal Server Error"):
            _handle_response(resp)

    def test_rate_limit(self):
        from cli_anything.rms.utils.rms_backend import _handle_response

        resp = MagicMock()
        resp.status_code = 429
        resp.headers = {"Retry-After": "30"}
        with pytest.raises(RuntimeError, match="Rate limit"):
            _handle_response(resp)


class TestFiles:
    """Tests for file operations."""

    @patch("cli_anything.rms.core.files.requests.post")
    def test_upload_file(self, mock_post):
        from cli_anything.rms.core.files import upload_file

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True, "data": {"id": 99}}
        mock_post.return_value = mock_resp

        with patch("builtins.open", mock_open(read_data=b"file-content")):
            result = upload_file("test-token", "/tmp/test.bin")

        assert mock_post.called
        assert result["success"] is True


class TestDeviceIdZero:
    """Verify device_id=0 is not falsy-skipped."""

    @patch("cli_anything.rms.core.alerts.api_get")
    def test_alerts_device_id_zero(self, mock_get):
        from cli_anything.rms.core.alerts import list_alerts

        mock_get.return_value = {"success": True, "data": []}
        list_alerts("token", device_id=0)
        params = mock_get.call_args.kwargs.get("params", {})
        assert "device_id" in params

    @patch("cli_anything.rms.core.configs.api_get")
    def test_configs_device_id_zero(self, mock_get):
        from cli_anything.rms.core.configs import list_configs

        mock_get.return_value = {"success": True, "data": []}
        list_configs("token", device_id=0)
        params = mock_get.call_args.kwargs.get("params", {})
        assert "device_id" in params

    @patch("cli_anything.rms.core.logs.api_get")
    def test_logs_device_id_zero(self, mock_get):
        from cli_anything.rms.core.logs import list_logs

        mock_get.return_value = {"success": True, "data": []}
        list_logs("token", device_id=0)
        params = mock_get.call_args.kwargs.get("params", {})
        assert "device_id" in params
