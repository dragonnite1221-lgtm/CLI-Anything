# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestMeetingCommands:
    """Test meeting CLI commands with mocked API."""

    def test_create_meeting(self, runner, mock_config):
        """meeting create should call API and show result."""
        mock_meeting = {
            "id": 12345,
            "uuid": "uuid-abc",
            "topic": "Test Standup",
            "type": 2,
            "status": "waiting",
            "start_time": "2025-06-01T10:00:00Z",
            "duration": 30,
            "timezone": "UTC",
            "agenda": "",
            "join_url": "https://zoom.us/j/12345",
            "start_url": "https://zoom.us/s/12345",
            "password": "abc123",
            "settings": {
                "auto_recording": "none",
                "waiting_room": False,
                "join_before_host": False,
                "mute_upon_entry": True,
            },
            "created_at": "2025-05-30T09:00:00Z",
        }

        with patch(
            "cli_anything.zoom.core.meetings.api_post", return_value=mock_meeting
        ):
            result = runner.invoke(
                cli,
                [
                    "meeting",
                    "create",
                    "--topic",
                    "Test Standup",
                    "--duration",
                    "30",
                ],
            )

        assert result.exit_code == 0
        assert "Test Standup" in result.output
        assert "12345" in result.output

    def test_list_meetings(self, runner, mock_config):
        """meeting list should show meetings."""
        mock_list = {
            "total_records": 1,
            "page_count": 1,
            "page_number": 1,
            "page_size": 30,
            "meetings": [
                {
                    "id": 12345,
                    "topic": "Weekly Sync",
                    "type": 2,
                    "start_time": "2025-06-01T10:00:00Z",
                    "duration": 60,
                    "timezone": "UTC",
                    "join_url": "https://zoom.us/j/12345",
                    "created_at": "2025-05-30T09:00:00Z",
                }
            ],
        }

        with patch("cli_anything.zoom.core.meetings.api_get", return_value=mock_list):
            result = runner.invoke(cli, ["meeting", "list"])

        assert result.exit_code == 0
        assert "Weekly Sync" in result.output

    def test_get_meeting_info(self, runner, mock_config):
        """meeting info should show meeting details."""
        mock_meeting = {
            "id": 12345,
            "uuid": "uuid-abc",
            "topic": "Standup",
            "type": 2,
            "status": "waiting",
            "start_time": "2025-06-01T10:00:00Z",
            "duration": 30,
            "timezone": "UTC",
            "agenda": "Daily standup",
            "join_url": "https://zoom.us/j/12345",
            "start_url": "https://zoom.us/s/12345",
            "password": "pass",
            "settings": {
                "auto_recording": "cloud",
                "waiting_room": True,
                "join_before_host": False,
                "mute_upon_entry": True,
            },
            "created_at": "2025-05-30T09:00:00Z",
        }

        with patch(
            "cli_anything.zoom.core.meetings.api_get", return_value=mock_meeting
        ):
            result = runner.invoke(cli, ["meeting", "info", "12345"])

        assert result.exit_code == 0
        assert "Standup" in result.output

    def test_delete_meeting(self, runner, mock_config):
        """meeting delete should confirm and delete."""
        with patch(
            "cli_anything.zoom.core.meetings.api_delete",
            return_value={"status": "success"},
        ):
            result = runner.invoke(
                cli,
                [
                    "meeting",
                    "delete",
                    "12345",
                    "--confirm",
                ],
            )

        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

    def test_update_meeting(self, runner, mock_config):
        """meeting update should patch meeting fields."""
        with patch("cli_anything.zoom.core.meetings.api_patch"):
            result = runner.invoke(
                cli,
                [
                    "meeting",
                    "update",
                    "12345",
                    "--topic",
                    "Updated Topic",
                    "--duration",
                    "45",
                ],
            )

        assert result.exit_code == 0
        assert "updated" in result.output.lower()
