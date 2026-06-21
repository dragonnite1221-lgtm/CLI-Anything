# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


class _TestAnalyticsMixin1:
    @pytest.mark.parametrize(
        ("command", "expected_reason"),
        [
            ("/usr/local/bin/gemini --prompt fix tests", "gemini-process"),
            ("/usr/local/bin/copilot agent", "copilot-process"),
            ("/usr/local/bin/auggie --print review", "auggie-process"),
            ("/opt/augment/bin/augment", "augment-process"),
            ("/usr/local/bin/ampcode fix build", "amp-process"),
            ("/usr/local/bin/opencode agent create", "opencode-process"),
            ("/usr/local/bin/kilo auth", "kilo-process"),
            ("/usr/local/bin/qodo chat", "qodo-process"),
            ("/usr/local/bin/kiro /agent create", "kiro-process"),
        ],
    )
    @patch("cli_hub.analytics._parent_process_commands")
    def test_detect_agent_from_expanded_parent_process_names(self, mock_cmds, command, expected_reason):
        mock_cmds.return_value = [command]
        with patch.dict(os.environ, {}, clear=True):
            context = detect_invocation_context()
            assert context["is_agent"] is True
            assert context["reason"] == expected_reason
            assert expected_reason in context["signals"]
    @patch("cli_hub.analytics._parent_process_commands", return_value=[])
    def test_detect_not_agent_clean_env(self, mock_cmds):
        """Clean env with a tty should not detect as agent."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.isatty.return_value = True
                assert _detect_is_agent() is False
    @patch("cli_hub.analytics._parent_process_commands", return_value=[])
    def test_detect_non_tty_is_agent(self, mock_cmds):
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.isatty.return_value = False
                context = detect_invocation_context()
                assert context["is_agent"] is True
                assert context["traffic_type"] == "agent"
                assert context["category"] == "scripted_client"
                assert context["reason"] == "stdin-not-tty"
    @patch("cli_hub.analytics._send_event")
    def test_track_visit_uses_detection_context(self, mock_send):
        detection = {
            "is_agent": True,
            "traffic_type": "agent",
            "category": "agent_tool",
            "reason": "codex-process",
            "signals": ["codex-process", "stdin-not-tty"],
            "stdin_tty": False,
            "is_interactive": False,
        }
        with patch.dict(os.environ, {}, clear=True):
            track_visit(command="search", detection=detection)
            import time
            time.sleep(0.2)
            payload = mock_send.call_args[0][0]
            assert payload["properties"]["command"] == "search"
            assert payload["properties"]["agent_reason"] == "codex-process"
            assert payload["properties"]["agent_category"] == "agent_tool"
            assert payload["properties"]["agent_signals"] == ["codex-process", "stdin-not-tty"]
            assert payload["properties"]["stdin_tty"] is False
            assert payload["properties"]["is_interactive"] is False
    @patch("cli_hub.analytics._send_event")
    def test_first_run_sends_event(self, mock_send, tmp_path):
        """First invocation sends cli-hub-installed event."""
        with patch.dict(os.environ, {"HOME": str(tmp_path)}, clear=False):
            track_first_run()
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["event"] == "cli-anything-hub-installed"
            assert payload["properties"]["$current_url"] == "https://clianything.cc/cli-anything-hub/installed"
            # Marker file should now exist
            assert (tmp_path / ".cli-hub" / ".first_run_sent").exists()
    @patch("cli_hub.analytics._send_event")
    def test_first_run_skips_if_marker_exists(self, mock_send, tmp_path):
        """Second invocation does NOT send cli-hub-installed event."""
        cli_hub_dir = tmp_path / ".cli-hub"
        cli_hub_dir.mkdir()
        (cli_hub_dir / ".first_run_sent").write_text("0.1.0")
        with patch.dict(os.environ, {"HOME": str(tmp_path)}, clear=False):
            track_first_run()
            import time
            time.sleep(0.2)
            mock_send.assert_not_called()
