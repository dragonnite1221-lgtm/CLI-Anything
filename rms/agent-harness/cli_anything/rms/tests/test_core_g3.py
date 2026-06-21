# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestRemoteAccess:
    @patch("cli_anything.rms.core.remote_access.api_get")
    def test_list_sessions(self, mock_get):
        from cli_anything.rms.core.remote_access import list_sessions

        mock_get.return_value = {"success": True, "data": [{"id": 1}]}
        result = list_sessions("token")
        mock_get.assert_called_once()
        assert result["success"] is True

    @patch("cli_anything.rms.core.remote_access.api_get")
    def test_list_sessions_by_device(self, mock_get):
        from cli_anything.rms.core.remote_access import list_sessions

        mock_get.return_value = {"success": True, "data": []}
        list_sessions("token", device_id="42")
        call_args = mock_get.call_args
        params = call_args.kwargs.get("params") or call_args[1].get("params", {})
        assert params.get("device_id") == "42"

    @patch("cli_anything.rms.core.remote_access.api_get")
    def test_get_session(self, mock_get):
        from cli_anything.rms.core.remote_access import get_session

        mock_get.return_value = {"success": True, "data": {"id": 3, "status": "active"}}
        result = get_session("token", "3")
        assert result["data"]["status"] == "active"

    @patch("cli_anything.rms.core.remote_access.api_post")
    def test_create_session(self, mock_post):
        from cli_anything.rms.core.remote_access import create_session

        mock_post.return_value = {"success": True, "data": {"id": 4, "device_id": "42"}}
        result = create_session("token", {"device_id": "42", "type": "ssh"})
        assert result["data"]["device_id"] == "42"

    @patch("cli_anything.rms.core.remote_access.api_delete")
    def test_delete_session(self, mock_delete):
        from cli_anything.rms.core.remote_access import delete_session

        mock_delete.return_value = {"success": True}
        result = delete_session("token", "3")
        assert result["success"] is True


class TestLogs:
    @patch("cli_anything.rms.core.logs.api_get")
    def test_list_logs(self, mock_get):
        from cli_anything.rms.core.logs import list_logs

        mock_get.return_value = {"success": True, "data": [{"id": 1}]}
        result = list_logs("token")
        mock_get.assert_called_once()
        assert result["success"] is True

    @patch("cli_anything.rms.core.logs.api_get")
    def test_list_logs_by_device(self, mock_get):
        from cli_anything.rms.core.logs import list_logs

        mock_get.return_value = {"success": True, "data": []}
        list_logs("token", device_id="42")
        call_args = mock_get.call_args
        params = call_args.kwargs.get("params") or call_args[1].get("params", {})
        assert params.get("device_id") == "42"

    @patch("cli_anything.rms.core.logs.api_get")
    def test_get_log(self, mock_get):
        from cli_anything.rms.core.logs import get_log

        mock_get.return_value = {"success": True, "data": {"id": 7, "message": "boot"}}
        result = get_log("token", "7")
        assert result["data"]["id"] == 7

    @patch("cli_anything.rms.core.logs.api_delete")
    def test_delete_log(self, mock_delete):
        from cli_anything.rms.core.logs import delete_log

        mock_delete.return_value = {"success": True}
        result = delete_log("token", "7")
        assert result["success"] is True


class TestCredits:
    @patch("cli_anything.rms.core.credits.api_get")
    def test_list_credits(self, mock_get):
        from cli_anything.rms.core.credits import list_credits

        mock_get.return_value = {"success": True, "data": [{"id": 1, "amount": 100}]}
        result = list_credits("token")
        mock_get.assert_called_once()
        assert result["data"][0]["amount"] == 100

    @patch("cli_anything.rms.core.credits.api_post")
    def test_transfer_credits(self, mock_post):
        from cli_anything.rms.core.credits import transfer_credits

        mock_post.return_value = {"success": True, "data": {"transferred": 50}}
        result = transfer_credits("token", {"amount": 50, "to_company": "2"})
        assert result["data"]["transferred"] == 50

    @patch("cli_anything.rms.core.credits.api_get")
    def test_list_transfer_codes(self, mock_get):
        from cli_anything.rms.core.credits import list_transfer_codes

        mock_get.return_value = {"success": True, "data": [{"code": "ABC123"}]}
        result = list_transfer_codes("token")
        assert result["data"][0]["code"] == "ABC123"
