# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestSessionOperations:
    def test_list_sessions(self, iterm2_connection):
        """List sessions returns a list."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.session import list_sessions

        result = run_iterm2(list_sessions)
        assert isinstance(result, list)
        assert len(result) >= 1
        print(f"\n  Sessions: {len(result)}")
        for s in result:
            print(f"    {s['session_id']}  name={s['name']}")

    def test_send_text_and_read_screen(self, iterm2_connection):
        """Send a command to a session and verify screen output."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import create_window, close_window
        from cli_anything.iterm2_ctl.core.session import (
            list_sessions,
            send_text,
            get_screen_contents,
        )

        w = run_iterm2(create_window)
        wid = w["window_id"]
        sid = w["session_id"]
        try:
            # Send a distinctive command
            marker = "CLI_TEST_MARKER_12345"
            run_iterm2(send_text, sid, f"echo {marker}\n", suppress_broadcast=False)
            time.sleep(0.5)  # let the shell process it

            # Read screen
            screen = run_iterm2(get_screen_contents, sid)
            assert "lines" in screen
            assert screen["total_lines"] > 0
            all_text = "\n".join(screen["lines"])
            assert marker in all_text, f"Marker not found in screen:\n{all_text[:500]}"
            print(f"\n  Screen read OK — found marker '{marker}'")
            print(f"  Artifact: session {sid}, {screen['returned_lines']} lines")
        finally:
            run_iterm2(close_window, wid, force=True)

    def test_split_pane(self, iterm2_connection):
        """Split a pane horizontally and verify new session created."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import create_window, close_window
        from cli_anything.iterm2_ctl.core.session import split_pane, list_sessions

        w = run_iterm2(create_window)
        wid = w["window_id"]
        sid = w["session_id"]
        try:
            result = run_iterm2(split_pane, sid, vertical=False)
            assert "new_session_id" in result
            new_sid = result["new_session_id"]
            assert new_sid != sid
            print(f"\n  Split pane: original={sid}, new={new_sid}")

            # Verify both sessions exist
            sessions = run_iterm2(list_sessions, window_id=wid)
            session_ids = [s["session_id"] for s in sessions]
            assert sid in session_ids
            assert new_sid in session_ids
        finally:
            run_iterm2(close_window, wid, force=True)


class TestProfileOperations:
    def test_list_profiles(self, iterm2_connection):
        """List profiles returns ≥ 1 profile."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.profile import list_profiles

        result = run_iterm2(list_profiles)
        assert isinstance(result, list)
        assert len(result) >= 1
        print(f"\n  Profiles: {len(result)}")
        for p in result:
            print(f"    {p['name']}")

    def test_list_color_presets(self, iterm2_connection):
        """List color presets returns a list."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.profile import list_color_presets

        result = run_iterm2(list_color_presets)
        assert isinstance(result, list)
        print(f"\n  Color presets: {len(result)}")
        if result:
            print(f"  Sample: {result[:3]}")


class TestArrangementOperations:
    def test_arrangement_save_list_restore(self, iterm2_connection):
        """Save, list, and restore an arrangement."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.arrangement import (
            save_arrangement,
            list_arrangements,
            restore_arrangement,
        )

        name = "cli-test-arrangement-tmp"
        try:
            # Save current state
            saved = run_iterm2(save_arrangement, name)
            assert saved["saved"] is True
            print(f"\n  Saved arrangement: '{name}'")

            # Verify it appears in list
            arrangements = run_iterm2(list_arrangements)
            assert name in arrangements
            print(f"  Found in list: {arrangements}")

            # Restore it
            restored = run_iterm2(restore_arrangement, name)
            assert restored["restored"] is True
            print(f"  Restored arrangement: '{name}'")
        finally:
            # No cleanup API for arrangements — leave it (small footprint)
            pass
