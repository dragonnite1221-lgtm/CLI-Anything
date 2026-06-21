# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTmuxCore(unittest.TestCase):
    """Unit tests for core/tmux.py logic that doesn't need a live connection."""

    def test_resolve_connection_empty_raises(self):
        """_resolve_connection raises RuntimeError when no connections exist."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import _resolve_connection

            mock_conn = MagicMock()

            with patch(
                "cli_anything.iterm2_ctl.core.tmux._ensure_app_and_connections",
                new=AsyncMock(return_value=[]),
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    await _resolve_connection(mock_conn, None)
                self.assertIn("tmux -CC", str(ctx.exception))

        asyncio.run(_run())

    def test_resolve_connection_by_id_not_found(self):
        """_resolve_connection raises ValueError for unknown connection ID."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import _resolve_connection

            mock_conn_obj = MagicMock()
            mock_conn_obj.connection_id = "real-id"

            with patch(
                "cli_anything.iterm2_ctl.core.tmux._ensure_app_and_connections",
                new=AsyncMock(return_value=[mock_conn_obj]),
            ):
                with self.assertRaises(ValueError) as ctx:
                    await _resolve_connection(MagicMock(), "wrong-id")
                self.assertIn("real-id", str(ctx.exception))

        asyncio.run(_run())

    def test_resolve_connection_returns_first_when_no_id(self):
        """_resolve_connection returns the first connection when ID is None."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import _resolve_connection

            c1 = MagicMock()
            c1.connection_id = "conn-1"
            c2 = MagicMock()
            c2.connection_id = "conn-2"

            with patch(
                "cli_anything.iterm2_ctl.core.tmux._ensure_app_and_connections",
                new=AsyncMock(return_value=[c1, c2]),
            ):
                result = await _resolve_connection(MagicMock(), None)
                self.assertEqual(result.connection_id, "conn-1")

        asyncio.run(_run())

    def test_list_connections_empty(self):
        """list_connections returns empty list when no tmux connections."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import list_connections

            with patch(
                "cli_anything.iterm2_ctl.core.tmux._ensure_app_and_connections",
                new=AsyncMock(return_value=[]),
            ):
                result = await list_connections(MagicMock())
                self.assertEqual(result, [])

        asyncio.run(_run())

    def test_list_connections_formats_result(self):
        """list_connections returns dicts with expected keys."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import list_connections

            mock_session = MagicMock()
            mock_session.session_id = "sess-1"
            mock_session.name = "bash"

            mock_conn = MagicMock()
            mock_conn.connection_id = "user@host"
            mock_conn.owning_session = mock_session

            with patch(
                "cli_anything.iterm2_ctl.core.tmux._ensure_app_and_connections",
                new=AsyncMock(return_value=[mock_conn]),
            ):
                result = await list_connections(MagicMock())
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["connection_id"], "user@host")
                self.assertEqual(result[0]["owning_session_id"], "sess-1")
                self.assertEqual(result[0]["owning_session_name"], "bash")

        asyncio.run(_run())

    def test_send_command_returns_output(self):
        """send_command returns connection_id, command, and output."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import send_command

            mock_tc = MagicMock()
            mock_tc.connection_id = "user@host"
            mock_tc.async_send_command = AsyncMock(return_value="session1\nsession2\n")

            with patch(
                "cli_anything.iterm2_ctl.core.tmux._resolve_connection",
                new=AsyncMock(return_value=mock_tc),
            ):
                result = await send_command(MagicMock(), "list-sessions")
                self.assertEqual(result["command"], "list-sessions")
                self.assertEqual(result["output"], "session1\nsession2\n")
                self.assertEqual(result["connection_id"], "user@host")

        asyncio.run(_run())

    def test_set_window_visible_on(self):
        """set_window_visible calls async_set_tmux_window_visible with correct args."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import set_window_visible

            mock_tc = MagicMock()
            mock_tc.connection_id = "user@host"
            mock_tc.async_set_tmux_window_visible = AsyncMock()

            with patch(
                "cli_anything.iterm2_ctl.core.tmux._resolve_connection",
                new=AsyncMock(return_value=mock_tc),
            ):
                result = await set_window_visible(MagicMock(), "@1", True)
                mock_tc.async_set_tmux_window_visible.assert_awaited_once_with(
                    "@1", True
                )
                self.assertEqual(result["tmux_window_id"], "@1")
                self.assertTrue(result["visible"])

        asyncio.run(_run())
