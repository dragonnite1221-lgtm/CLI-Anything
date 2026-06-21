# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    def test_session_create(self, tmp_path):
        from cli_anything.rms.core.session import Session

        sf = str(tmp_path / "session.json")
        s = Session(session_file=sf)
        assert s.status()["history_count"] == 0

    def test_session_save_load(self, tmp_path):
        from cli_anything.rms.core.session import Session

        sf = str(tmp_path / "session.json")
        s = Session(session_file=sf)
        s.set_last_device("42")
        s.save_history("devices list", {"count": 5})

        s2 = Session(session_file=sf)
        assert s2.last_device_id == "42"
        assert len(s2.history) == 1

    def test_session_clear(self, tmp_path):
        from cli_anything.rms.core.session import Session

        sf = str(tmp_path / "session.json")
        s = Session(session_file=sf)
        s.set_last_device("42")
        s.save_history("test", {})
        s.clear()
        assert s.last_device_id is None
        assert len(s.history) == 0

    def test_session_history_limit(self, tmp_path):
        from cli_anything.rms.core.session import Session

        sf = str(tmp_path / "session.json")
        s = Session(session_file=sf)
        for i in range(60):
            s.save_history(f"cmd-{i}", {})
        assert len(s.history) == 50


class TestUsers:
    @patch("cli_anything.rms.core.users.api_get")
    def test_list_users(self, mock_get):
        from cli_anything.rms.core.users import list_users

        mock_get.return_value = {
            "success": True,
            "data": [{"id": 1, "email": "a@b.com"}],
        }
        result = list_users("token")
        mock_get.assert_called_once()
        assert result["data"][0]["email"] == "a@b.com"

    @patch("cli_anything.rms.core.users.api_get")
    def test_get_user(self, mock_get):
        from cli_anything.rms.core.users import get_user

        mock_get.return_value = {"success": True, "data": {"id": 5, "email": "u@b.com"}}
        result = get_user("token", "5")
        assert result["data"]["id"] == 5

    @patch("cli_anything.rms.core.users.api_post")
    def test_invite_user(self, mock_post):
        from cli_anything.rms.core.users import invite_user

        mock_post.return_value = {
            "success": True,
            "data": {"id": 6, "email": "new@b.com"},
        }
        result = invite_user("token", {"email": "new@b.com"})
        assert result["data"]["email"] == "new@b.com"

    @patch("cli_anything.rms.core.users.api_put")
    def test_update_user(self, mock_put):
        from cli_anything.rms.core.users import update_user

        mock_put.return_value = {"success": True, "data": {"id": 5, "name": "Updated"}}
        result = update_user("token", "5", {"name": "Updated"})
        assert result["data"]["name"] == "Updated"

    @patch("cli_anything.rms.core.users.api_delete")
    def test_delete_user(self, mock_delete):
        from cli_anything.rms.core.users import delete_user

        mock_delete.return_value = {"success": True}
        result = delete_user("token", "5")
        assert result["success"] is True


class TestConfigs:
    @patch("cli_anything.rms.core.configs.api_get")
    def test_list_configs(self, mock_get):
        from cli_anything.rms.core.configs import list_configs

        mock_get.return_value = {"success": True, "data": [{"id": 1}]}
        result = list_configs("token")
        mock_get.assert_called_once()
        assert result["success"] is True

    @patch("cli_anything.rms.core.configs.api_get")
    def test_list_configs_by_device(self, mock_get):
        from cli_anything.rms.core.configs import list_configs

        mock_get.return_value = {"success": True, "data": []}
        list_configs("token", device_id="42")
        call_args = mock_get.call_args
        params = call_args.kwargs.get("params") or call_args[1].get("params", {})
        assert params.get("device_id") == "42"

    @patch("cli_anything.rms.core.configs.api_get")
    def test_get_config(self, mock_get):
        from cli_anything.rms.core.configs import get_config

        mock_get.return_value = {"success": True, "data": {"id": 10, "name": "cfg1"}}
        result = get_config("token", "10")
        assert result["data"]["id"] == 10

    @patch("cli_anything.rms.core.configs.api_put")
    def test_update_config(self, mock_put):
        from cli_anything.rms.core.configs import update_config

        mock_put.return_value = {"success": True, "data": {"id": 10, "value": "new"}}
        result = update_config("token", "10", {"value": "new"})
        assert result["success"] is True
