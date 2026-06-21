# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestWireMockClient(unittest.TestCase):
    def setUp(self):
        from cli_anything.wiremock.utils.client import WireMockClient

        self.client = WireMockClient(host="testhost", port=9090, scheme="https")

    def test_base_url_construction(self):
        self.assertEqual(self.client.base_url(), "https://testhost:9090/__admin")

    def test_base_url_defaults(self):
        from cli_anything.wiremock.utils.client import WireMockClient

        c = WireMockClient()
        self.assertEqual(c.base_url(), "http://localhost:8080/__admin")

    @patch("requests.get")
    def test_get_passes_auth_and_timeout(self, mock_get):
        mock_get.return_value = _mock_response(200, {})
        self.client.auth = ("user", "pass")
        self.client.get("/mappings")
        mock_get.assert_called_once_with(
            "https://testhost:9090/__admin/mappings",
            auth=("user", "pass"),
            timeout=30,
        )

    @patch("requests.post")
    def test_post_sends_json(self, mock_post):
        mock_post.return_value = _mock_response(200, {})
        self.client.post("/mappings", json={"key": "value"})
        mock_post.assert_called_once_with(
            "https://testhost:9090/__admin/mappings",
            json={"key": "value"},
            auth=None,
            timeout=30,
        )

    @patch("requests.put")
    def test_put_sends_json(self, mock_put):
        mock_put.return_value = _mock_response(200, {})
        self.client.put("/mappings/abc", json={"id": "abc"})
        mock_put.assert_called_once()

    @patch("requests.delete")
    def test_delete(self, mock_delete):
        mock_delete.return_value = _mock_response(200, {})
        self.client.delete("/mappings/abc")
        mock_delete.assert_called_once()

    @patch("requests.patch")
    def test_patch(self, mock_patch):
        mock_patch.return_value = _mock_response(200, {})
        self.client.patch("/mappings/abc", json={"name": "x"})
        mock_patch.assert_called_once()

    @patch("requests.get")
    def test_is_alive_true(self, mock_get):
        mock_get.return_value = _mock_response(200, {})
        self.assertTrue(self.client.is_alive())

    @patch("requests.get")
    def test_is_alive_false_on_non_200(self, mock_get):
        mock_get.return_value = _mock_response(503, {})
        self.assertFalse(self.client.is_alive())

    @patch("requests.get")
    def test_is_alive_false_on_exception(self, mock_get):
        mock_get.side_effect = ConnectionError("refused")
        self.assertFalse(self.client.is_alive())


class TestSession(unittest.TestCase):
    def test_from_env_defaults(self):
        from cli_anything.wiremock.core.session import Session

        env = {}
        with patch.dict(os.environ, env, clear=False):
            # Remove keys if they exist so defaults are used
            for k in [
                "WIREMOCK_HOST",
                "WIREMOCK_PORT",
                "WIREMOCK_SCHEME",
                "WIREMOCK_USER",
                "WIREMOCK_PASSWORD",
            ]:
                os.environ.pop(k, None)
            s = Session.from_env()
        self.assertEqual(s.host, "localhost")
        self.assertEqual(s.port, 8080)
        self.assertEqual(s.scheme, "http")
        self.assertIsNone(s.username)
        self.assertIsNone(s.password)

    def test_from_env_reads_env_vars(self):
        from cli_anything.wiremock.core.session import Session

        with patch.dict(
            os.environ,
            {
                "WIREMOCK_HOST": "myhost",
                "WIREMOCK_PORT": "9999",
                "WIREMOCK_SCHEME": "https",
                "WIREMOCK_USER": "admin",
                "WIREMOCK_PASSWORD": "secret",
            },
        ):
            s = Session.from_env()
        self.assertEqual(s.host, "myhost")
        self.assertEqual(s.port, 9999)
        self.assertEqual(s.scheme, "https")
        self.assertEqual(s.username, "admin")
        self.assertEqual(s.password, "secret")

    def test_auth_returns_tuple_when_both_set(self):
        from cli_anything.wiremock.core.session import Session

        s = Session(username="u", password="p")
        self.assertEqual(s.auth(), ("u", "p"))

    def test_auth_returns_none_when_partial(self):
        from cli_anything.wiremock.core.session import Session

        s = Session(username="u")  # no password
        self.assertIsNone(s.auth())

    def test_auth_returns_none_when_empty(self):
        from cli_anything.wiremock.core.session import Session

        s = Session()
        self.assertIsNone(s.auth())


if __name__ == "__main__":
    unittest.main()
