# ruff: noqa: F403, F405, E501
from .test_full_e2e_helpers import *  # noqa: F403


class TestAppStatus:
    def test_app_status(self, iterm2_connection):
        """Get app status — should return window count."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        import iterm2

        async def _get_status(conn):
            app = await iterm2.async_get_app(conn)
            return {"window_count": len(app.windows)}

        result = run_iterm2(_get_status)
        assert "window_count" in result
        assert result["window_count"] >= 0
        print(f"\n  App status: {result['window_count']} window(s)")

    def test_get_current_context(self, iterm2_connection):
        """Get current focused window/tab/session."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import get_current_window

        result = run_iterm2(get_current_window)
        # May be None if no window focused, but should not raise
        print(f"\n  Current context: {result}")
        if result is not None:
            assert "window_id" in result


class TestWorkspaceSnapshot:
    def test_workspace_snapshot_structure(self, iterm2_connection):
        """snapshot returns session_count and sessions list with required keys."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.session import workspace_snapshot

        result = run_iterm2(workspace_snapshot)
        assert "session_count" in result
        assert "sessions" in result
        assert isinstance(result["sessions"], list)
        assert result["session_count"] == len(result["sessions"])
        print(f"\n  Snapshot: {result['session_count']} session(s)")
        for s in result["sessions"]:
            assert "session_id" in s
            assert "name" in s
            assert "window_id" in s
            assert "tab_id" in s
            assert "path" in s
            assert "pid" in s
            assert "process" in s
            assert "role" in s
            assert "last_line" in s
            print(
                f"    {s['session_id']}  name={s['name']}  "
                f"process={s['process']}  path={s['path']}"
            )

    def test_workspace_snapshot_process_populated(self, iterm2_connection):
        """process field should be a non-empty string for sessions with a running shell."""
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.session import workspace_snapshot

        result = run_iterm2(workspace_snapshot)
        if result["session_count"] > 0:
            # At least one session should have a process name
            processes = [s["process"] for s in result["sessions"] if s["process"]]
            assert len(processes) > 0, (
                "Expected at least one session with a process name"
            )
            print(f"\n  Processes found: {processes}")


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v", "-s"])
