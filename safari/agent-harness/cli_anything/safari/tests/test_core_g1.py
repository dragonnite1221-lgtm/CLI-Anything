# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCallForwarding:
    """Verify backend.call() forwards args, strips None, and unwraps results."""

    def test_strips_none_args_before_call(self):
        from cli_anything.safari.utils import safari_backend as backend

        captured: dict = {}

        async def fake_call_tool(tool_name, arguments):
            captured["tool"] = tool_name
            captured["args"] = arguments
            result = MagicMock()
            item = MagicMock()
            item.text = '{"ok": true}'
            result.content = [item]
            return result

        with patch.object(backend, "_call_tool", side_effect=fake_call_tool):
            result = backend.call(
                "safari_navigate",
                url="https://example.com",
                selector=None,
                x=None,
                y=42,
            )

        assert captured["tool"] == "safari_navigate"
        # None values must be stripped; non-None must be forwarded.
        assert captured["args"] == {"url": "https://example.com", "y": 42}
        # The MCP CallToolResult must be unwrapped to the inner JSON.
        assert result == {"ok": True}

    def test_passes_full_arg_set_when_none_omitted(self):
        from cli_anything.safari.utils import safari_backend as backend

        captured: dict = {}

        async def fake_call_tool(tool_name, arguments):
            captured["args"] = arguments
            result = MagicMock()
            result.content = []
            return result

        with patch.object(backend, "_call_tool", side_effect=fake_call_tool):
            backend.call("safari_click", ref="0_5", selector="#submit")

        assert captured["args"] == {"ref": "0_5", "selector": "#submit"}

    def test_unwraps_plain_text_when_not_json(self):
        from cli_anything.safari.utils import safari_backend as backend

        captured: dict = {}

        async def fake_call_tool(tool_name, arguments):
            captured["tool"] = tool_name
            captured["args"] = arguments
            result = MagicMock()
            item = MagicMock()
            item.text = "not a json string"
            result.content = [item]
            return result

        with patch.object(backend, "_call_tool", side_effect=fake_call_tool):
            # Note: safari_evaluate's parameter is "script", not "code".
            # This test doubles as a regression lock for the doc bug
            # where examples used --code by mistake.
            result = backend.call("safari_evaluate", script="document.title")

        assert captured["tool"] == "safari_evaluate"
        assert captured["args"] == {"script": "document.title"}
        assert result == "not a json string"


class TestSessionState:
    def test_session_defaults(self):
        from cli_anything.safari.core.session import Session

        s = Session()
        assert s.current_tab_index is None
        assert s.last_url == ""

    def test_set_url_updates_last_url(self):
        from cli_anything.safari.core.session import Session

        s = Session()
        s.set_url("https://example.com")
        assert s.last_url == "https://example.com"

    def test_set_tab_updates_current_tab(self):
        from cli_anything.safari.core.session import Session

        s = Session()
        s.set_tab(3)
        assert s.current_tab_index == 3

    def test_status_contains_expected_keys(self):
        from cli_anything.safari.core.session import Session

        s = Session()
        s.set_url("https://example.com")
        s.set_tab(2)

        status = s.status()
        assert status["last_url"] == "https://example.com"
        assert status["current_tab_index"] == 2
        assert "daemon_mode" not in status  # removed in v1

    def test_status_empty_url_returns_sentinel(self):
        from cli_anything.safari.core.session import Session

        s = Session()
        # last_url not set yet — status() should return the sentinel
        # so REPL display has something readable.
        status = s.status()
        assert status["last_url"] == "(no navigation yet)"
        assert status["current_tab_index"] is None
