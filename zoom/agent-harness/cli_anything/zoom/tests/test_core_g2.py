# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestParticipantCommands:
    """Test participant CLI commands."""

    def test_add_participant(self, runner, mock_config):
        """participant add should register a user."""
        mock_result = {
            "registrant_id": "reg_123",
            "id": 12345,
            "topic": "Meeting",
            "email": "user@example.com",
            "join_url": "https://zoom.us/j/12345?tk=reg_123",
            "start_time": "",
        }

        with patch(
            "cli_anything.zoom.core.participants.api_post", return_value=mock_result
        ):
            result = runner.invoke(
                cli,
                [
                    "participant",
                    "add",
                    "12345",
                    "--email",
                    "user@example.com",
                    "--first-name",
                    "John",
                ],
            )

        assert result.exit_code == 0
        assert "user@example.com" in result.output

    def test_list_registrants(self, runner, mock_config):
        """participant list should show registrants."""
        mock_result = {
            "total_records": 1,
            "registrants": [
                {
                    "id": "reg_123",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "status": "approved",
                    "create_time": "2025-05-30T09:00:00Z",
                }
            ],
        }

        with patch(
            "cli_anything.zoom.core.participants.api_get", return_value=mock_result
        ):
            result = runner.invoke(
                cli,
                [
                    "participant",
                    "list",
                    "12345",
                ],
            )

        assert result.exit_code == 0
        assert "user@example.com" in result.output


class TestRecordingCommands:
    """Test recording CLI commands."""

    def test_list_recordings(self, runner, mock_config):
        """recording list should show cloud recordings."""
        mock_result = {
            "total_records": 1,
            "meetings": [
                {
                    "id": 12345,
                    "uuid": "uuid-abc",
                    "topic": "Recorded Meeting",
                    "start_time": "2025-06-01T10:00:00Z",
                    "duration": 60,
                    "total_size": 104857600,
                    "recording_count": 2,
                    "recording_files": [
                        {
                            "id": "file_1",
                            "file_type": "MP4",
                            "file_extension": "MP4",
                            "file_size": 83886080,
                            "status": "completed",
                            "recording_start": "2025-06-01T10:00:00Z",
                            "recording_end": "2025-06-01T11:00:00Z",
                            "download_url": "https://zoom.us/rec/download/abc",
                        },
                    ],
                }
            ],
        }

        with patch(
            "cli_anything.zoom.core.recordings.api_get", return_value=mock_result
        ):
            result = runner.invoke(cli, ["recording", "list"])

        assert result.exit_code == 0
        assert "Recorded Meeting" in result.output

    def test_get_recording_files(self, runner, mock_config):
        """recording files should show recording details."""
        mock_result = {
            "id": 12345,
            "uuid": "uuid-abc",
            "topic": "My Meeting",
            "start_time": "2025-06-01T10:00:00Z",
            "duration": 60,
            "total_size": 104857600,
            "recording_files": [
                {
                    "id": "file_1",
                    "file_type": "MP4",
                    "file_extension": "MP4",
                    "file_size": 83886080,
                    "status": "completed",
                    "download_url": "https://zoom.us/rec/download/abc",
                    "play_url": "https://zoom.us/rec/play/abc",
                    "recording_start": "2025-06-01T10:00:00Z",
                    "recording_end": "2025-06-01T11:00:00Z",
                },
            ],
        }

        with patch(
            "cli_anything.zoom.core.recordings.api_get", return_value=mock_result
        ):
            result = runner.invoke(cli, ["recording", "files", "12345"])

        assert result.exit_code == 0
        assert "MP4" in result.output
