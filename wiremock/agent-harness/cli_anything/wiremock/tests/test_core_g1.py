# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestStubsManager(unittest.TestCase):
    def setUp(self):
        from cli_anything.wiremock.utils.client import WireMockClient
        from cli_anything.wiremock.core.stubs import StubsManager

        self.client = WireMockClient()
        self.mgr = StubsManager(self.client)

    @patch("requests.get")
    def test_list_no_params(self, mock_get):
        mock_get.return_value = _mock_response(200, {"mappings": [], "total": 0})
        result = self.mgr.list()
        self.assertEqual(result["total"], 0)
        call_kwargs = mock_get.call_args
        # params should not include limit/offset when not provided
        self.assertNotIn("limit", call_kwargs.kwargs.get("params", {}))

    @patch("requests.get")
    def test_list_with_limit_and_offset(self, mock_get):
        mock_get.return_value = _mock_response(200, {"mappings": [], "total": 0})
        self.mgr.list(limit=10, offset=5)
        params = mock_get.call_args.kwargs.get("params", {})
        self.assertEqual(params["limit"], 10)
        self.assertEqual(params["offset"], 5)

    @patch("requests.get")
    def test_get_stub(self, mock_get):
        stub_data = {"id": "abc-123", "request": {"method": "GET"}}
        mock_get.return_value = _mock_response(200, stub_data)
        result = self.mgr.get("abc-123")
        self.assertEqual(result["id"], "abc-123")
        mock_get.assert_called_once()
        assert "/mappings/abc-123" in mock_get.call_args.args[0]

    @patch("requests.post")
    def test_create_stub(self, mock_post):
        created = {"id": "new-id", "request": {"method": "GET", "url": "/foo"}}
        mock_post.return_value = _mock_response(201, created)
        mapping = {
            "request": {"method": "GET", "url": "/foo"},
            "response": {"status": 200},
        }
        result = self.mgr.create(mapping)
        self.assertEqual(result["id"], "new-id")
        posted_json = mock_post.call_args.kwargs["json"]
        self.assertEqual(posted_json["request"]["url"], "/foo")

    @patch("requests.delete")
    def test_delete_stub(self, mock_delete):
        mock_delete.return_value = _mock_response(200, {})
        self.mgr.delete("abc-123")
        mock_delete.assert_called_once()
        assert "/mappings/abc-123" in mock_delete.call_args.args[0]

    @patch("requests.post")
    def test_reset(self, mock_post):
        mock_post.return_value = _mock_response(200, {})
        self.mgr.reset()
        assert "/mappings/reset" in mock_post.call_args.args[0]

    @patch("requests.post")
    def test_save(self, mock_post):
        mock_post.return_value = _mock_response(200, {})
        self.mgr.save()
        assert "/mappings/save" in mock_post.call_args.args[0]

    @patch("requests.post")
    def test_quick_stub_no_body(self, mock_post):
        mock_post.return_value = _mock_response(200, {"id": "q1"})
        self.mgr.quick_stub("GET", "/ping", 200)
        sent = mock_post.call_args.kwargs["json"]
        self.assertEqual(sent["request"]["method"], "GET")
        self.assertEqual(sent["request"]["url"], "/ping")
        self.assertEqual(sent["response"]["status"], 200)
        self.assertNotIn("body", sent["response"])

    @patch("requests.post")
    def test_quick_stub_with_body(self, mock_post):
        mock_post.return_value = _mock_response(200, {"id": "q2"})
        self.mgr.quick_stub("POST", "/data", 201, body='{"ok":true}')
        sent = mock_post.call_args.kwargs["json"]
        self.assertEqual(sent["response"]["body"], '{"ok":true}')
        self.assertIn("Content-Type", sent["response"]["headers"])

    @patch("requests.post")
    def test_quick_stub_method_uppercased(self, mock_post):
        mock_post.return_value = _mock_response(200, {"id": "q3"})
        self.mgr.quick_stub("get", "/health", 200)
        sent = mock_post.call_args.kwargs["json"]
        self.assertEqual(sent["request"]["method"], "GET")

    @patch("requests.post")
    def test_import_stubs(self, mock_post):
        mock_post.return_value = _mock_response(200, {"mappings": []})
        result = self.mgr.import_stubs({"mappings": []})
        assert "/mappings/import" in mock_post.call_args.args[0]
        self.assertIn("mappings", result)

    @patch("requests.post")
    def test_find_by_metadata(self, mock_post):
        mock_post.return_value = _mock_response(200, {"mappings": []})
        pattern = {"matchesJsonPath": {"expression": "$.name", "equalTo": "x"}}
        self.mgr.find_by_metadata(pattern)
        assert "/mappings/find-by-metadata" in mock_post.call_args.args[0]
