# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestFiltering:
    def test_get_status(self):
        c = make_client()
        resp = mock_response({"enabled": True, "filters": []})
        with patch.object(c.session, "get", return_value=resp):
            result = filtering.get_status(c)
            assert result["enabled"] is True

    def test_add_filter(self):
        c = make_client()
        resp = mock_response({})
        with patch.object(c.session, "post", return_value=resp) as mock_post:
            filtering.add_filter(c, url="http://example.com/list.txt", name="Test")
            body = mock_post.call_args.kwargs["json"]
            assert body["url"] == "http://example.com/list.txt"
            assert body["name"] == "Test"
            assert body["whitelist"] is False

    def test_remove_filter(self):
        c = make_client()
        resp = mock_response({})
        with patch.object(c.session, "post", return_value=resp) as mock_post:
            filtering.remove_filter(c, url="http://example.com/list.txt")
            body = mock_post.call_args.kwargs["json"]
            assert body["url"] == "http://example.com/list.txt"

    def test_set_enabled(self):
        c = make_client()
        status_resp = mock_response({"enabled": False, "interval": 48})
        post_resp = mock_response({})
        with patch.object(c.session, "get", return_value=status_resp):
            with patch.object(c.session, "post", return_value=post_resp) as mock_post:
                filtering.set_enabled(c, enabled=True)
                body = mock_post.call_args.kwargs["json"]
                assert body["enabled"] is True
                assert body["interval"] == 48


class TestBlocking:
    def test_parental_status(self):
        c = make_client()
        resp = mock_response({"enabled": False})
        with patch.object(c.session, "get", return_value=resp):
            result = blocking.parental_status(c)
            assert result == {"enabled": False}

    def test_parental_enable(self):
        c = make_client()
        resp = mock_response()
        with patch.object(c.session, "post", return_value=resp) as mock_post:
            blocking.parental_enable(c)
            assert "/parental/enable" in mock_post.call_args.args[0]

    def test_safebrowsing_status(self):
        c = make_client()
        resp = mock_response({"enabled": True})
        with patch.object(c.session, "get", return_value=resp):
            result = blocking.safebrowsing_status(c)
            assert result["enabled"] is True


class TestClients:
    def test_list_clients(self):
        c = make_client()
        data = {
            "clients": [{"name": "PC", "ids": ["192.168.1.10"]}],
            "auto_clients": [],
        }
        resp = mock_response(data)
        with patch.object(c.session, "get", return_value=resp):
            result = clients.list_clients(c)
            assert len(result["clients"]) == 1

    def test_add_client(self):
        c = make_client()
        resp = mock_response({})
        with patch.object(c.session, "post", return_value=resp) as mock_post:
            clients.add_client(c, name="MyPC", ids=["192.168.1.100"])
            body = mock_post.call_args.kwargs["json"]
            assert body["name"] == "MyPC"
            assert "192.168.1.100" in body["ids"]


class TestRewrite:
    def test_list_rewrites(self):
        c = make_client()
        data = [{"domain": "myserver.local", "answer": "192.168.1.50"}]
        resp = mock_response(data)
        with patch.object(c.session, "get", return_value=resp):
            result = rewrite.list_rewrites(c)
            assert len(result) == 1
            assert result[0]["domain"] == "myserver.local"

    def test_add_rewrite(self):
        c = make_client()
        resp = mock_response({})
        with patch.object(c.session, "post", return_value=resp) as mock_post:
            rewrite.add_rewrite(c, domain="myserver.local", answer="192.168.1.50")
            body = mock_post.call_args.kwargs["json"]
            assert body["domain"] == "myserver.local"
            assert body["answer"] == "192.168.1.50"
