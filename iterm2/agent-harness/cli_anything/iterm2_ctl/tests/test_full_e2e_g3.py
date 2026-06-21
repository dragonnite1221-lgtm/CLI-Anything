# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestTmuxOperations:
    def test_list_connections_always_works(self, iterm2_connection):
        """list_connections returns a list (possibly empty) without error."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tmux import list_connections

        result = run_iterm2(list_connections)
        assert isinstance(result, list)
        print(f"\n  Tmux connections: {len(result)}")
        for c in result:
            print(f"    {c['connection_id']}  gateway={c['owning_session_id']}")

    def test_list_tmux_tabs_always_works(self, iterm2_connection):
        """list_tmux_tabs returns a list (possibly empty) without error."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tmux import list_tmux_tabs

        result = run_iterm2(list_tmux_tabs)
        assert isinstance(result, list)
        print(f"\n  Tmux-backed tabs: {len(result)}")
        for t in result:
            print(
                f"    tab={t['tab_id']} tmux-window={t['tmux_window_id']} "
                f"connection={t['tmux_connection_id']}"
            )

    def test_send_command_list_sessions(self, tmux_connection):
        """Send 'list-sessions' to an active tmux connection."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tmux import send_command

        conn_id = tmux_connection[0]["connection_id"]
        result = run_iterm2(send_command, "list-sessions", connection_id=conn_id)
        assert "connection_id" in result
        assert "command" in result
        assert "output" in result
        assert result["command"] == "list-sessions"
        # Output must be non-empty (at least one session is active since we're in it)
        assert len(result["output"]) > 0
        print(f"\n  tmux list-sessions output:\n{result['output']}")

    def test_send_command_list_windows(self, tmux_connection):
        """Send 'list-windows' — verifies arbitrary tmux command dispatch."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tmux import send_command

        result = run_iterm2(send_command, "list-windows")
        assert result["output"]
        print(f"\n  tmux list-windows:\n{result['output']}")

    def test_send_command_display_message(self, tmux_connection):
        """Send 'display-message' to get tmux server info."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tmux import send_command

        result = run_iterm2(send_command, "display-message -p '#{session_name}'")
        assert "output" in result
        print(f"\n  tmux session name: {result['output'].strip()!r}")

    def test_create_and_verify_tmux_window(self, tmux_connection):
        """Create a tmux window and verify it appears as an iTerm2 tab."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tmux import create_window, list_tmux_tabs
        from cli_anything.iterm2_ctl.core.window import close_window

        result = run_iterm2(create_window)
        assert "window_id" in result
        assert "tab_id" in result
        assert result["tab_id"] is not None
        print(
            f"\n  Created tmux window: window={result['window_id']} "
            f"tab={result['tab_id']} session={result['session_id']}"
        )

        # Verify the new tab appears in the tmux-tabs list
        time.sleep(0.3)
        tabs = run_iterm2(list_tmux_tabs)
        tab_ids = [t["tab_id"] for t in tabs]
        assert result["tab_id"] in tab_ids, (
            f"New tab {result['tab_id']} not in tmux tabs: {tab_ids}"
        )
        print(f"  Confirmed new tab {result['tab_id']} in tmux tabs list")

        # Clean up
        run_iterm2(close_window, result["window_id"], force=True)

    def test_set_window_visible_roundtrip(self, tmux_connection):
        """Hide then show a tmux window and verify no errors."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tmux import (
            create_window,
            list_tmux_tabs,
            set_window_visible,
        )
        from cli_anything.iterm2_ctl.core.window import close_window

        # Create a tmux window to play with
        created = run_iterm2(create_window)
        wid = created["window_id"]
        tid = created["tab_id"]

        try:
            time.sleep(0.3)
            # Find its tmux_window_id
            tabs = run_iterm2(list_tmux_tabs)
            tmux_wid = next(
                (t["tmux_window_id"] for t in tabs if t["tab_id"] == tid), None
            )
            if tmux_wid is None:
                pytest.skip(
                    "Could not find tmux_window_id for new tab — may vary by iTerm2 version"
                )

            # Hide
            r_hide = run_iterm2(set_window_visible, tmux_wid, False)
            assert r_hide["visible"] is False
            print(f"\n  Hidden tmux window {tmux_wid}")

            # Show
            r_show = run_iterm2(set_window_visible, tmux_wid, True)
            assert r_show["visible"] is True
            print(f"  Shown tmux window {tmux_wid}")
        finally:
            # Hiding a tmux window removes the corresponding iTerm2 window,
            # so close_window may raise ValueError if the window is already gone.
            try:
                run_iterm2(close_window, wid, force=True)
            except (ValueError, RuntimeError):
                pass  # Already removed — that's fine
