# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestCLISubprocess(unittest.TestCase):
    """Tests that exercise CLI argument parsing without a live WireMock server."""

    def test_top_level_help(self):
        result = _run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("stub", result.stdout)
        self.assertIn("request", result.stdout)
        self.assertIn("scenario", result.stdout)
        self.assertIn("record", result.stdout)
        self.assertIn("settings", result.stdout)

    def test_stub_group_help(self):
        result = _run("stub", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("list", result.stdout)
        self.assertIn("create", result.stdout)
        self.assertIn("quick", result.stdout)
        self.assertIn("delete", result.stdout)

    def test_stub_list_help(self):
        result = _run("stub", "list", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--limit", result.stdout)
        self.assertIn("--offset", result.stdout)

    def test_stub_quick_help(self):
        result = _run("stub", "quick", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("METHOD", result.stdout)
        self.assertIn("URL", result.stdout)
        self.assertIn("STATUS", result.stdout)
        self.assertIn("--body", result.stdout)

    def test_request_group_help(self):
        result = _run("request", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("list", result.stdout)
        self.assertIn("find", result.stdout)
        self.assertIn("count", result.stdout)
        self.assertIn("unmatched", result.stdout)
        self.assertIn("reset", result.stdout)

    def test_scenario_group_help(self):
        result = _run("scenario", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("list", result.stdout)
        self.assertIn("set", result.stdout)
        self.assertIn("reset", result.stdout)

    def test_record_group_help(self):
        result = _run("record", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("start", result.stdout)
        self.assertIn("stop", result.stdout)
        self.assertIn("status", result.stdout)
        self.assertIn("snapshot", result.stdout)

    def test_settings_group_help(self):
        result = _run("settings", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("get", result.stdout)
        self.assertIn("version", result.stdout)

    def test_status_help(self):
        result = _run("status", "--help")
        self.assertEqual(result.returncode, 0)

    def test_global_json_flag_in_help(self):
        result = _run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--json", result.stdout)

    def test_global_host_flag_in_help(self):
        result = _run("--help")
        self.assertIn("--host", result.stdout)

    def test_global_port_flag_in_help(self):
        result = _run("--help")
        self.assertIn("--port", result.stdout)

    def test_record_start_help_shows_match_header(self):
        result = _run("record", "start", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--match-header", result.stdout)

    def test_status_fails_gracefully_when_no_server(self):
        """status should exit non-zero or print 'stopped' — not crash."""
        result = _run(
            "status",
            env_extras={
                "WIREMOCK_HOST": "127.0.0.1",
                "WIREMOCK_PORT": "19999",  # nothing listening here
            },
        )
        # Either it prints "stopped" (exit 0) or exits with 1 — both are acceptable
        # It must NOT raise an unhandled exception
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        if result.returncode == 0:
            self.assertIn("stopped", result.stdout)

    def test_status_json_fails_gracefully_when_no_server(self):
        """--json status should output valid JSON even when server is unreachable."""
        result = _run(
            "--json",
            "status",
            env_extras={
                "WIREMOCK_HOST": "127.0.0.1",
                "WIREMOCK_PORT": "19999",
            },
        )
        self.assertNotIn("Traceback", result.stdout)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            self.assertIn("status", data)


if __name__ == "__main__":
    unittest.main()
