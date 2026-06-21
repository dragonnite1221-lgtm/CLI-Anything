# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestJsonOutput:
    """Test --json flag produces valid JSON."""

    def test_meeting_list_json(self, runner, mock_config):
        """--json flag should produce valid JSON output."""
        mock_list = {
            "total_records": 1,
            "page_count": 1,
            "page_number": 1,
            "page_size": 30,
            "meetings": [
                {
                    "id": 99999,
                    "topic": "JSON Test",
                    "type": 2,
                    "start_time": "",
                    "duration": 30,
                    "timezone": "UTC",
                    "join_url": "",
                    "created_at": "",
                }
            ],
        }

        with patch("cli_anything.zoom.core.meetings.api_get", return_value=mock_list):
            result = runner.invoke(cli, ["--json", "meeting", "list"])

        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert parsed["total_records"] == 1
        assert parsed["meetings"][0]["topic"] == "JSON Test"

    def test_auth_status_json(self, runner, mock_config):
        """auth status with --json should return valid JSON."""
        result = runner.invoke(cli, ["--json", "auth", "status"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert "configured" in parsed
        assert "authenticated" in parsed
