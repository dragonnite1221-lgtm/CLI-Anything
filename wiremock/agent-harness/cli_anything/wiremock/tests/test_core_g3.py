# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestRecordingManager(unittest.TestCase):
    def setUp(self):
        from cli_anything.wiremock.utils.client import WireMockClient
        from cli_anything.wiremock.core.recording import RecordingManager

        self.client = WireMockClient()
        self.mgr = RecordingManager(self.client)

    @patch("requests.post")
    def test_start_no_headers(self, mock_post):
        mock_post.return_value = _mock_response(200, {"status": "Recording"})
        result = self.mgr.start("https://api.example.com")
        sent = mock_post.call_args.kwargs["json"]
        self.assertEqual(sent["targetBaseUrl"], "https://api.example.com")
        self.assertNotIn("captureHeaders", sent)

    @patch("requests.post")
    def test_start_with_headers(self, mock_post):
        mock_post.return_value = _mock_response(200, {"status": "Recording"})
        self.mgr.start(
            "https://api.example.com", headers_to_match=["Authorization", "X-Api-Key"]
        )
        sent = mock_post.call_args.kwargs["json"]
        self.assertIn("captureHeaders", sent)
        self.assertIn("Authorization", sent["captureHeaders"])
        self.assertIn("X-Api-Key", sent["captureHeaders"])
        self.assertTrue(sent["captureHeaders"]["Authorization"]["caseInsensitive"])

    @patch("requests.post")
    def test_stop(self, mock_post):
        mock_post.return_value = _mock_response(200, {"mappings": [{"id": "x"}]})
        result = self.mgr.stop()
        assert "/recordings/stop" in mock_post.call_args.args[0]
        self.assertIn("mappings", result)

    @patch("requests.get")
    def test_status(self, mock_get):
        mock_get.return_value = _mock_response(200, {"status": "Recording"})
        result = self.mgr.status()
        assert "/recordings/status" in mock_get.call_args.args[0]
        self.assertEqual(result["status"], "Recording")

    @patch("requests.post")
    def test_snapshot(self, mock_post):
        mock_post.return_value = _mock_response(200, {"mappings": []})
        result = self.mgr.snapshot()
        assert "/recordings/snapshot" in mock_post.call_args.args[0]
        self.assertIn("mappings", result)

    @patch("requests.post")
    def test_snapshot_with_spec(self, mock_post):
        mock_post.return_value = _mock_response(200, {"mappings": []})
        self.mgr.snapshot(spec={"persist": False})
        sent = mock_post.call_args.kwargs["json"]
        self.assertFalse(sent["persist"])


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        from cli_anything.wiremock.utils.client import WireMockClient
        from cli_anything.wiremock.core.settings import SettingsManager

        self.client = WireMockClient()
        self.mgr = SettingsManager(self.client)

    @patch("requests.get")
    def test_get(self, mock_get):
        mock_get.return_value = _mock_response(200, {"fixedDelay": 0})
        result = self.mgr.get()
        assert "/settings" in mock_get.call_args.args[0]
        self.assertIn("fixedDelay", result)

    @patch("requests.put")
    def test_update(self, mock_put):
        mock_put.return_value = _mock_response(200, {"fixedDelay": 500})
        result = self.mgr.update({"fixedDelay": 500})
        sent = mock_put.call_args.kwargs["json"]
        self.assertEqual(sent["fixedDelay"], 500)

    @patch("requests.get")
    def test_get_version(self, mock_get):
        mock_get.return_value = _mock_response(200, {"version": "3.3.1"})
        result = self.mgr.get_version()
        assert "/version" in mock_get.call_args.args[0]
        self.assertEqual(result["version"], "3.3.1")
