# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestRequestsLog(unittest.TestCase):
    def setUp(self):
        from cli_anything.wiremock.utils.client import WireMockClient
        from cli_anything.wiremock.core.requests_log import RequestsLog

        self.client = WireMockClient()
        self.log = RequestsLog(self.client)

    @patch("requests.get")
    def test_list(self, mock_get):
        mock_get.return_value = _mock_response(200, {"serveEvents": [], "total": 0})
        result = self.log.list()
        self.assertIn("serveEvents", result)

    @patch("requests.get")
    def test_list_with_limit(self, mock_get):
        mock_get.return_value = _mock_response(200, {"serveEvents": [], "total": 0})
        self.log.list(limit=5)
        params = mock_get.call_args.kwargs.get("params", {})
        self.assertEqual(params["limit"], 5)

    @patch("requests.post")
    def test_find(self, mock_post):
        mock_post.return_value = _mock_response(200, {"requests": []})
        pattern = {"method": "GET", "url": "/foo"}
        result = self.log.find(pattern)
        assert "/requests/find" in mock_post.call_args.args[0]
        self.assertIn("requests", result)

    @patch("requests.post")
    def test_count(self, mock_post):
        mock_post.return_value = _mock_response(200, {"count": 3})
        pattern = {"method": "POST"}
        result = self.log.count(pattern)
        self.assertEqual(result["count"], 3)
        assert "/requests/count" in mock_post.call_args.args[0]

    @patch("requests.get")
    def test_unmatched(self, mock_get):
        mock_get.return_value = _mock_response(200, {"requests": []})
        result = self.log.unmatched()
        assert "/requests/unmatched" in mock_get.call_args.args[0]

    @patch("requests.get")
    def test_near_misses_unmatched(self, mock_get):
        mock_get.return_value = _mock_response(200, {"nearMisses": []})
        result = self.log.near_misses_unmatched()
        assert "/requests/unmatched/near-misses" in mock_get.call_args.args[0]

    @patch("requests.delete")
    def test_reset(self, mock_delete):
        mock_delete.return_value = _mock_response(200, {})
        self.log.reset()
        assert "/requests" in mock_delete.call_args.args[0]


class TestScenariosManager(unittest.TestCase):
    def setUp(self):
        from cli_anything.wiremock.utils.client import WireMockClient
        from cli_anything.wiremock.core.scenarios import ScenariosManager

        self.client = WireMockClient()
        self.mgr = ScenariosManager(self.client)

    @patch("requests.get")
    def test_list(self, mock_get):
        mock_get.return_value = _mock_response(200, {"scenarios": []})
        result = self.mgr.list()
        self.assertIn("scenarios", result)
        assert "/scenarios" in mock_get.call_args.args[0]

    @patch("requests.put")
    def test_set_state(self, mock_put):
        mock_put.return_value = _mock_response(200, {})
        self.mgr.set_state("login-flow", "logged-in")
        assert "/scenarios/login-flow/state" in mock_put.call_args.args[0]
        sent = mock_put.call_args.kwargs["json"]
        self.assertEqual(sent["state"], "logged-in")

    @patch("requests.post")
    def test_reset_all(self, mock_post):
        mock_post.return_value = _mock_response(200, {})
        self.mgr.reset_all()
        assert "/scenarios/reset" in mock_post.call_args.args[0]
