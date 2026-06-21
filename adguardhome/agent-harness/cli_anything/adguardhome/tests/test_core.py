# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestAdGuardHomeClient:
    def test_client_init_default(self):
        c = AdGuardHomeClient()
        assert c.base_url == "http://localhost:3000/control"
        assert c.host == "localhost"
        assert c.port == 3000

    def test_client_init_with_auth(self):
        c = AdGuardHomeClient(username="admin", password="pass")
        assert c.session.auth == ("admin", "pass")

    def test_client_init_no_auth(self):
        c = AdGuardHomeClient()
        assert c.session.auth is None

    def test_client_url_construction(self):
        c = AdGuardHomeClient(host="192.168.1.1", port=8080)
        assert c._url("/status") == "http://192.168.1.1:8080/control/status"
        assert c._url("status") == "http://192.168.1.1:8080/control/status"

    def test_get_success(self):
        c = make_client()
        resp = mock_response({"running": True})
        with patch.object(c.session, "get", return_value=resp) as mock_get:
            result = c.get("/status")
            assert result == {"running": True}
            mock_get.assert_called_once()

    def test_get_empty_response(self):
        c = make_client()
        resp = mock_response()
        with patch.object(c.session, "get", return_value=resp):
            result = c.get("/restart")
            assert result == {}

    def test_post_json(self):
        c = make_client()
        resp = mock_response({})
        with patch.object(c.session, "post", return_value=resp) as mock_post:
            c.post(
                "/filtering/add_url",
                {"url": "http://example.com/list.txt", "name": "Test"},
            )
            call_kwargs = mock_post.call_args
            assert call_kwargs.kwargs.get("json") == {
                "url": "http://example.com/list.txt",
                "name": "Test",
            }

    def test_post_empty(self):
        c = make_client()
        resp = mock_response()
        with patch.object(c.session, "post", return_value=resp) as mock_post:
            result = c.post("/restart")
            assert result == {}
            mock_post.assert_called_once()

    def test_connection_error_raises_runtime(self):
        c = make_client()
        with patch.object(
            c.session, "get", side_effect=requests.exceptions.ConnectionError("refused")
        ):
            with pytest.raises(RuntimeError) as exc_info:
                c.get("/status")
            assert "Cannot connect to AdGuardHome" in str(exc_info.value)
            assert (
                "docker run" in str(exc_info.value).lower()
                or "docker" in str(exc_info.value).lower()
            )


class TestProject:
    def test_load_config_defaults(self, tmp_path):
        result = project.load_config(config_path=tmp_path / "nonexistent.json")
        assert result["host"] == "localhost"
        assert result["port"] == 3000
        assert result["username"] == ""
        assert result["password"] == ""

    def test_load_config_from_file(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(
            json.dumps(
                {
                    "host": "192.168.1.1",
                    "port": 8080,
                    "username": "admin",
                    "password": "secret",
                }
            )
        )
        result = project.load_config(config_path=cfg_file)
        assert result["host"] == "192.168.1.1"
        assert result["port"] == 8080
        assert result["username"] == "admin"

    def test_load_config_env_override(self, tmp_path, monkeypatch):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"host": "from-file", "port": 3000}))
        monkeypatch.setenv("AGH_HOST", "from-env")
        monkeypatch.setenv("AGH_PORT", "9000")
        result = project.load_config(config_path=cfg_file)
        assert result["host"] == "from-env"
        assert result["port"] == 9000

    def test_save_config(self, tmp_path):
        path = tmp_path / "config.json"
        saved = project.save_config("myhost", 4000, "user", "pass", config_path=path)
        assert saved == path
        data = json.loads(path.read_text())
        assert data["host"] == "myhost"
        assert data["port"] == 4000
