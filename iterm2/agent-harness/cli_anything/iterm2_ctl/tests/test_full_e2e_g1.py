# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestWindowOperations:
    def test_list_windows(self, iterm2_connection):
        """List windows returns a list."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import list_windows

        result = run_iterm2(list_windows)
        assert isinstance(result, list)
        print(f"\n  Windows: {len(result)}")
        for w in result:
            print(f"    {w['window_id']}  tabs={w['tab_count']}")

    def test_create_and_close_window(self, iterm2_connection):
        """Create a window, verify it appears in the list, then close it."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import (
            list_windows,
            create_window,
            close_window,
        )

        # Create
        created = run_iterm2(create_window)
        assert "window_id" in created
        wid = created["window_id"]
        print(f"\n  Created window: {wid}")

        # Verify it appears in list
        windows = run_iterm2(list_windows)
        ids = [w["window_id"] for w in windows]
        assert wid in ids, f"Window {wid} not in list: {ids}"

        # Close
        closed = run_iterm2(close_window, wid, force=True)
        assert closed["closed"] is True
        print(f"  Closed window: {wid}")

        # Verify removed
        time.sleep(0.3)
        windows_after = run_iterm2(list_windows)
        ids_after = [w["window_id"] for w in windows_after]
        assert wid not in ids_after

    def test_window_frame(self, iterm2_connection):
        """Get window frame returns numeric x/y/w/h."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import (
            create_window,
            close_window,
            get_window_frame,
        )

        created = run_iterm2(create_window)
        wid = created["window_id"]
        try:
            frame = run_iterm2(get_window_frame, wid)
            assert "x" in frame
            assert "y" in frame
            assert "width" in frame
            assert "height" in frame
            assert frame["width"] > 0
            assert frame["height"] > 0
            print(
                f"\n  Frame: x={frame['x']} y={frame['y']} "
                f"w={frame['width']} h={frame['height']}"
            )
        finally:
            run_iterm2(close_window, wid, force=True)


class TestTabOperations:
    def test_list_tabs(self, iterm2_connection):
        """List tabs returns a list."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.tab import list_tabs

        result = run_iterm2(list_tabs)
        assert isinstance(result, list)
        print(f"\n  Tabs: {len(result)}")

    def test_create_and_close_tab(self, iterm2_connection):
        """Create a tab in a new window, verify it, then close."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import create_window, close_window
        from cli_anything.iterm2_ctl.core.tab import create_tab, list_tabs

        # Create window for test
        w = run_iterm2(create_window)
        wid = w["window_id"]
        try:
            # Create extra tab
            tab = run_iterm2(create_tab, window_id=wid)
            assert "tab_id" in tab
            tid = tab["tab_id"]
            print(f"\n  Created tab: {tid} in window {wid}")

            # Verify it appears
            tabs = run_iterm2(list_tabs, window_id=wid)
            tab_ids = [t["tab_id"] for t in tabs]
            assert tid in tab_ids
        finally:
            run_iterm2(close_window, wid, force=True)
