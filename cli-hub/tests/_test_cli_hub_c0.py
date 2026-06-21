# ruff: noqa: F403, F405, E501
from ._test_cli_hub_base import *  # noqa: F403


class _TestAnalyticsMixin0:
    """Tests for analytics.py — opt-out, event firing, event names."""
    def test_analytics_enabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            assert _is_enabled()
    def test_analytics_disabled_by_env(self):
        with patch.dict(os.environ, {"CLI_HUB_NO_ANALYTICS": "1"}):
            assert not _is_enabled()
    def test_analytics_disabled_by_true(self):
        with patch.dict(os.environ, {"CLI_HUB_NO_ANALYTICS": "true"}):
            assert not _is_enabled()
    @patch("cli_hub.analytics._send_event")
    def test_track_event_sends_request(self, mock_send):
        with patch.dict(os.environ, {}, clear=True):
            track_event("test-event", data={"key": "value"})
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["event"] == "test-event"
            assert payload["properties"]["hostname"] == "clianything.cc"
            assert payload["properties"]["source"] == "cli"
    @patch("cli_hub.analytics._send_event")
    def test_track_event_noop_when_disabled(self, mock_send):
        with patch.dict(os.environ, {"CLI_HUB_NO_ANALYTICS": "1"}):
            track_event("test-event")
            import time
            time.sleep(0.2)
            mock_send.assert_not_called()
    @patch("cli_hub.analytics._send_event")
    def test_track_event_supports_umami_provider(self, mock_send):
        with patch.dict(os.environ, {"CLI_HUB_ANALYTICS_PROVIDER": "umami"}, clear=False):
            track_event("test-event")
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["payload"]["name"] == "test-event"
            assert payload["payload"]["hostname"] == "clianything.cc"
    @patch("cli_hub.analytics._send_event")
    def test_track_install_event_name_is_flat(self, mock_send):
        """cli-install event name is static; CLI name lives in properties.cli."""
        with patch.dict(os.environ, {}, clear=True):
            track_install("gimp", "1.0.0")
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["event"] == "cli-install"
            assert payload["properties"]["$current_url"] == "https://clianything.cc/cli-anything-hub/install/gimp"
            assert payload["properties"]["cli"] == "gimp"
            assert payload["properties"]["version"] == "1.0.0"
            assert "platform" in payload["properties"]
    @patch("cli_hub.analytics._send_event")
    def test_track_uninstall_event_name_is_flat(self, mock_send):
        """cli-uninstall event name is static; CLI name lives in properties.cli."""
        with patch.dict(os.environ, {}, clear=True):
            analytics_track_uninstall("blender")
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["event"] == "cli-uninstall"
            assert payload["properties"]["$current_url"] == "https://clianything.cc/cli-anything-hub/uninstall/blender"
            assert payload["properties"]["cli"] == "blender"
            assert "platform" in payload["properties"]
    @patch("cli_hub.analytics._send_event")
    def test_track_launch_fires(self, mock_send):
        """cli-launch event fires with the CLI name in properties."""
        from cli_hub.analytics import track_launch
        with patch.dict(os.environ, {}, clear=True):
            track_launch("gimp")
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["event"] == "cli-launch"
            assert payload["properties"]["cli"] == "gimp"
            assert payload["properties"]["$current_url"] == "https://clianything.cc/cli-anything-hub/launch/gimp"
    @patch("cli_hub.analytics._send_event")
    def test_track_visit_human(self, mock_send):
        """cli-hub call event sent when not detected as agent."""
        with patch.dict(os.environ, {}, clear=True):
            track_visit(is_agent=False)
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["event"] == "cli-hub call"
            assert payload["properties"]["$current_url"] == "https://clianything.cc/cli-anything-hub/call"
            assert payload["properties"]["command"] == "root"
            assert payload["properties"]["is_agent"] is False
            assert payload["properties"]["traffic_type"] == "human"
    @patch("cli_hub.analytics._send_event")
    def test_track_visit_agent(self, mock_send):
        """cli-hub call event captures the agent flag."""
        with patch.dict(os.environ, {}, clear=True):
            track_visit(is_agent=True, command="--version")
            import time
            time.sleep(0.2)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["event"] == "cli-hub call"
            assert payload["properties"]["command"] == "--version"
            assert payload["properties"]["is_agent"] is True
            assert payload["properties"]["traffic_type"] == "agent"
    def test_detect_agent_claude_code(self):
        with patch.dict(os.environ, {"CLAUDE_CODE": "1"}):
            assert _detect_is_agent() is True
    def test_detect_agent_codex(self):
        with patch.dict(os.environ, {"CODEX": "1"}):
            assert _detect_is_agent() is True
    @patch("cli_hub.analytics._parent_process_commands", return_value=["/usr/local/bin/codex --run"])
    def test_detect_agent_from_parent_process(self, mock_cmds):
        with patch.dict(os.environ, {}, clear=True):
            context = detect_invocation_context()
            assert context["is_agent"] is True
            assert context["reason"] == "codex-process"
            assert "codex-process" in context["signals"]
