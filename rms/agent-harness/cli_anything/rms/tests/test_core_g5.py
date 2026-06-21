# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestHotspots:
    @patch("cli_anything.rms.core.hotspots.api_get")
    def test_list_hotspots(self, mock_get):
        from cli_anything.rms.core.hotspots import list_hotspots

        mock_get.return_value = {"success": True, "data": [{"id": 1}]}
        result = list_hotspots("token")
        mock_get.assert_called_once()
        assert result["success"] is True

    @patch("cli_anything.rms.core.hotspots.api_get")
    def test_list_hotspots_by_device(self, mock_get):
        from cli_anything.rms.core.hotspots import list_hotspots

        mock_get.return_value = {"success": True, "data": []}
        list_hotspots("token", device_id="42")
        call_args = mock_get.call_args
        params = call_args.kwargs.get("params") or call_args[1].get("params", {})
        assert params.get("device_id") == "42"

    @patch("cli_anything.rms.core.hotspots.api_get")
    def test_get_hotspot(self, mock_get):
        from cli_anything.rms.core.hotspots import get_hotspot

        mock_get.return_value = {"success": True, "data": {"id": 1, "name": "Lobby"}}
        result = get_hotspot("token", "1")
        assert result["data"]["name"] == "Lobby"

    @patch("cli_anything.rms.core.hotspots.api_post")
    def test_create_hotspot(self, mock_post):
        from cli_anything.rms.core.hotspots import create_hotspot

        mock_post.return_value = {"success": True, "data": {"id": 2, "name": "Cafe"}}
        result = create_hotspot("token", {"name": "Cafe"})
        assert result["data"]["name"] == "Cafe"

    @patch("cli_anything.rms.core.hotspots.api_put")
    def test_update_hotspot(self, mock_put):
        from cli_anything.rms.core.hotspots import update_hotspot

        mock_put.return_value = {"success": True, "data": {"id": 1, "name": "Updated"}}
        result = update_hotspot("token", "1", {"name": "Updated"})
        assert result["data"]["name"] == "Updated"

    @patch("cli_anything.rms.core.hotspots.api_delete")
    def test_delete_hotspot(self, mock_delete):
        from cli_anything.rms.core.hotspots import delete_hotspot

        mock_delete.return_value = {"success": True}
        result = delete_hotspot("token", "1")
        assert result["success"] is True


class TestPasswords:
    @patch("cli_anything.rms.core.passwords.api_get")
    def test_get_password(self, mock_get):
        from cli_anything.rms.core.passwords import get_password

        mock_get.return_value = {
            "success": True,
            "data": {"device_id": "42", "password": "***"},
        }
        result = get_password("token", "42")
        assert result["data"]["device_id"] == "42"

    @patch("cli_anything.rms.core.passwords.api_put")
    def test_update_password(self, mock_put):
        from cli_anything.rms.core.passwords import update_password

        mock_put.return_value = {"success": True, "data": {"device_id": "42"}}
        result = update_password("token", "42", {"password": "newpass"})
        assert result["success"] is True


class TestSmtp:
    @patch("cli_anything.rms.core.smtp.api_get")
    def test_list_smtp_configs(self, mock_get):
        from cli_anything.rms.core.smtp import list_smtp_configs

        mock_get.return_value = {
            "success": True,
            "data": [{"id": 1, "host": "smtp.test"}],
        }
        result = list_smtp_configs("token")
        mock_get.assert_called_once()
        assert result["data"][0]["host"] == "smtp.test"

    @patch("cli_anything.rms.core.smtp.api_get")
    def test_get_smtp_config(self, mock_get):
        from cli_anything.rms.core.smtp import get_smtp_config

        mock_get.return_value = {
            "success": True,
            "data": {"id": 1, "host": "smtp.test"},
        }
        result = get_smtp_config("token", "1")
        assert result["data"]["id"] == 1

    @patch("cli_anything.rms.core.smtp.api_post")
    def test_create_smtp_config(self, mock_post):
        from cli_anything.rms.core.smtp import create_smtp_config

        mock_post.return_value = {
            "success": True,
            "data": {"id": 2, "host": "new.smtp"},
        }
        result = create_smtp_config("token", {"host": "new.smtp", "port": 587})
        assert result["data"]["host"] == "new.smtp"

    @patch("cli_anything.rms.core.smtp.api_put")
    def test_update_smtp_config(self, mock_put):
        from cli_anything.rms.core.smtp import update_smtp_config

        mock_put.return_value = {
            "success": True,
            "data": {"id": 1, "host": "updated.smtp"},
        }
        result = update_smtp_config("token", "1", {"host": "updated.smtp"})
        assert result["data"]["host"] == "updated.smtp"

    @patch("cli_anything.rms.core.smtp.api_delete")
    def test_delete_smtp_config(self, mock_delete):
        from cli_anything.rms.core.smtp import delete_smtp_config

        mock_delete.return_value = {"success": True}
        result = delete_smtp_config("token", "1")
        assert result["success"] is True
