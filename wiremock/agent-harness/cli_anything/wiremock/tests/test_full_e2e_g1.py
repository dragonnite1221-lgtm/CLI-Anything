# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestLiveServer(unittest.TestCase):
    """Tests against a live WireMock instance.

    Set WIREMOCK_URL=http://localhost:8080 before running.
    """

    @skip_no_server
    def setUp(self):
        """Reset WireMock state before each test."""
        _run("reset", input_text="y\n")  # confirm the prompt if any
        # Also try a clean reset via the full-reset command
        result = subprocess.run(
            CLI_CMD + ["reset"],
            capture_output=True,
            text=True,
            env={**os.environ, **self._env()},
        )
        # Ignore reset errors — server might already be clean

    def _env(self):
        from urllib.parse import urlparse

        parsed = urlparse(WIREMOCK_URL)
        return {
            "WIREMOCK_HOST": parsed.hostname or "localhost",
            "WIREMOCK_PORT": str(parsed.port or 8080),
            "WIREMOCK_SCHEME": parsed.scheme or "http",
        }

    @skip_no_server
    def test_status_running(self):
        result = _run("--json", "status")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "running")

    @skip_no_server
    def test_stub_list_empty(self):
        result = _run("--json", "stub", "list")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        # WireMock may have default stubs; just check the structure
        self.assertIn("mappings", data)

    @skip_no_server
    def test_stub_quick_create_and_list(self):
        # Create a stub
        result = _run(
            "--json",
            "stub",
            "quick",
            "GET",
            "/test-endpoint",
            "200",
            "--body",
            '{"hello":"world"}',
        )
        self.assertEqual(result.returncode, 0)
        created = json.loads(result.stdout)
        self.assertIn("id", created)
        stub_id = created["id"]
        self.assertIsNotNone(stub_id)

        # List and find it
        result = _run("--json", "stub", "list")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        ids = [m["id"] for m in data.get("mappings", [])]
        self.assertIn(stub_id, ids)

    @skip_no_server
    def test_stub_create_full_json(self):
        mapping = {
            "request": {"method": "POST", "url": "/api/orders"},
            "response": {
                "status": 201,
                "body": '{"id":42}',
                "headers": {"Content-Type": "application/json"},
            },
        }
        result = _run("--json", "stub", "create", json.dumps(mapping))
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("id", data)

    @skip_no_server
    def test_stub_get(self):
        # Create a stub first
        r = _run("--json", "stub", "quick", "GET", "/get-test", "200")
        stub_id = json.loads(r.stdout)["id"]

        result = _run("--json", "stub", "get", stub_id)
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["id"], stub_id)

    @skip_no_server
    def test_stub_delete(self):
        # Create then delete
        r = _run("--json", "stub", "quick", "GET", "/delete-me", "200")
        stub_id = json.loads(r.stdout)["id"]

        result = _run("--json", "stub", "delete", stub_id)
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "ok")

    @skip_no_server
    def test_stub_reset(self):
        # Create a stub, then reset
        _run("stub", "quick", "GET", "/ephemeral", "200")
        result = _run("--json", "stub", "reset")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "ok")

    @skip_no_server
    def test_request_list_and_reset(self):
        # List requests
        result = _run("--json", "request", "list")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("serveEvents", data)

        # Reset
        result = _run("--json", "request", "reset")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "ok")

    @skip_no_server
    def test_request_count(self):
        pattern = json.dumps({"method": "GET", "url": "/nonexistent"})
        result = _run("--json", "request", "count", pattern)
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("count", data)

    @skip_no_server
    def test_scenario_list(self):
        result = _run("--json", "scenario", "list")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("scenarios", data)

    @skip_no_server
    def test_scenario_reset(self):
        result = _run("--json", "scenario", "reset")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "ok")

    @skip_no_server
    def test_record_status(self):
        result = _run("--json", "record", "status")
        self.assertEqual(result.returncode, 0)
        # WireMock returns {"status": "NeverStarted"} or "Recording" or "Stopped"
        # just verify we got a valid response
        data = json.loads(result.stdout)
        self.assertIn("status", data)

    @skip_no_server
    def test_settings_version(self):
        result = _run("--json", "settings", "version")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("version", data)

    @skip_no_server
    def test_settings_get(self):
        result = _run("--json", "settings", "get")
        self.assertEqual(result.returncode, 0)
        # Should return a JSON object (no crash)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, dict)

    @skip_no_server
    def test_request_unmatched(self):
        result = _run("--json", "request", "unmatched")
        self.assertEqual(result.returncode, 0)
        # Just verify it returns valid JSON
        data = json.loads(result.stdout)
        self.assertIsInstance(data, dict)
