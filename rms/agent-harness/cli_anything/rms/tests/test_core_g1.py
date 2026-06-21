# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestDevices:
    """Tests for devices core module."""

    @patch("cli_anything.rms.core.devices.api_get")
    def test_list_devices(self, mock_get):
        from cli_anything.rms.core.devices import list_devices

        mock_get.return_value = {
            "success": True,
            "data": [{"id": 1, "name": "Router-1"}],
            "meta": {"total": 1},
        }

        result = list_devices("token")
        mock_get.assert_called_once()
        assert result["data"][0]["name"] == "Router-1"

    @patch("cli_anything.rms.core.devices.api_get")
    def test_list_devices_with_filters(self, mock_get):
        from cli_anything.rms.core.devices import list_devices

        mock_get.return_value = {"success": True, "data": [], "meta": {"total": 0}}

        list_devices("token", status="online", tag=["office"], limit=10, offset=5)
        call_args = mock_get.call_args
        params = call_args.kwargs.get("params") or call_args[1].get("params", {})
        assert params.get("status") == "online"

    @patch("cli_anything.rms.core.devices.api_get")
    def test_get_device(self, mock_get):
        from cli_anything.rms.core.devices import get_device

        mock_get.return_value = {
            "success": True,
            "data": {"id": 42, "name": "Gateway-42", "status": "online"},
        }

        result = get_device("token", "42")
        assert result["data"]["id"] == 42


class TestCompanies:
    @patch("cli_anything.rms.core.companies.api_get")
    def test_list_companies(self, mock_get):
        from cli_anything.rms.core.companies import list_companies

        mock_get.return_value = {"success": True, "data": [{"id": 1}]}
        result = list_companies("token")
        assert result["success"] is True

    @patch("cli_anything.rms.core.companies.api_post")
    def test_create_company(self, mock_post):
        from cli_anything.rms.core.companies import create_company

        mock_post.return_value = {"success": True, "data": {"id": 2, "name": "Acme"}}
        result = create_company("token", {"name": "Acme"})
        assert result["data"]["name"] == "Acme"


class TestTags:
    @patch("cli_anything.rms.core.tags.api_get")
    def test_list_tags(self, mock_get):
        from cli_anything.rms.core.tags import list_tags

        mock_get.return_value = {"success": True, "data": [{"id": 1, "name": "office"}]}
        result = list_tags("token")
        assert len(result["data"]) == 1

    @patch("cli_anything.rms.core.tags.api_post")
    def test_create_tag(self, mock_post):
        from cli_anything.rms.core.tags import create_tag

        mock_post.return_value = {"success": True, "data": {"id": 3, "name": "new-tag"}}
        result = create_tag("token", {"name": "new-tag"})
        assert result["data"]["name"] == "new-tag"


class TestAlerts:
    @patch("cli_anything.rms.core.alerts.api_get")
    def test_list_alerts(self, mock_get):
        from cli_anything.rms.core.alerts import list_alerts

        mock_get.return_value = {"success": True, "data": []}
        result = list_alerts("token")
        assert result["success"] is True

    @patch("cli_anything.rms.core.alerts.api_get")
    def test_list_alerts_by_device(self, mock_get):
        from cli_anything.rms.core.alerts import list_alerts

        mock_get.return_value = {"success": True, "data": []}
        list_alerts("token", device_id="42")
        call_args = mock_get.call_args
        params = call_args.kwargs.get("params") or call_args[1].get("params", {})
        assert params.get("device_id") == "42"


class TestLocation:
    @patch("cli_anything.rms.core.location.api_get")
    def test_get_location(self, mock_get):
        from cli_anything.rms.core.location import get_location

        mock_get.return_value = {
            "success": True,
            "data": {"latitude": 54.6872, "longitude": 25.2797},
        }
        result = get_location("token", "42")
        assert "latitude" in result["data"]
