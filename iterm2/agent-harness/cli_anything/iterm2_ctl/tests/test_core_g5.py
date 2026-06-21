# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPromptCore(unittest.TestCase):
    """Unit tests for core/prompt.py."""

    def test_prompt_to_dict_none(self):
        """_prompt_to_dict handles None (Shell Integration absent)."""
        from cli_anything.iterm2_ctl.core.prompt import _prompt_to_dict

        result = _prompt_to_dict(None)
        self.assertFalse(result["available"])

    def test_prompt_to_dict_with_mock(self):
        """_prompt_to_dict converts a mock prompt object to dict."""
        from cli_anything.iterm2_ctl.core.prompt import _prompt_to_dict

        mock_prompt = MagicMock()
        mock_prompt.unique_id = "uid-1"
        mock_prompt.command = "ls -la"
        mock_prompt.working_directory = "/home/user"
        mock_prompt.state = MagicMock()
        mock_prompt.state.name = "RUNNING"
        mock_prompt.prompt_range = None
        mock_prompt.command_range = MagicMock()
        mock_prompt.output_range = None
        result = _prompt_to_dict(mock_prompt)
        self.assertTrue(result["available"])
        self.assertEqual(result["command"], "ls -la")
        self.assertEqual(result["working_directory"], "/home/user")
        self.assertEqual(result["state"], "RUNNING")
        self.assertFalse(result["has_prompt_range"])
        self.assertTrue(result["has_command_range"])

    def test_get_last_prompt_returns_unavailable_for_none(self):
        """get_last_prompt returns available=False when API returns None."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.prompt import get_last_prompt

            with patch(
                "iterm2.async_get_last_prompt",
                new=AsyncMock(return_value=None),
            ):
                result = await get_last_prompt(MagicMock(), "sess-1")
                self.assertFalse(result["available"])

        asyncio.run(_run())

    def test_list_prompts_empty(self):
        """list_prompts returns empty list when no prompts recorded."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.prompt import list_prompts

            with patch(
                "iterm2.async_list_prompts",
                new=AsyncMock(return_value=[]),
            ):
                result = await list_prompts(MagicMock(), "sess-1")
                self.assertEqual(result["prompt_ids"], [])
                self.assertEqual(result["count"], 0)
                self.assertEqual(result["session_id"], "sess-1")

        asyncio.run(_run())


class TestTmuxBootstrap(unittest.TestCase):
    """Unit tests for core/tmux.bootstrap()."""

    def test_bootstrap_timeout_raises(self):
        """bootstrap raises RuntimeError when no connection appears in time."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import bootstrap

            mock_session = MagicMock()
            mock_session.async_send_text = AsyncMock()

            mock_tab = MagicMock()
            mock_tab.current_session = mock_session

            mock_window = MagicMock()
            mock_window.current_tab = mock_tab

            mock_app = MagicMock()
            mock_app.windows = [mock_window]

            with (
                patch("iterm2.async_get_app", new=AsyncMock(return_value=mock_app)),
                patch(
                    "iterm2.async_get_tmux_connections", new=AsyncMock(return_value=[])
                ),
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    await bootstrap(MagicMock(), timeout=0.1)
                self.assertIn("Timed out", str(ctx.exception))

        asyncio.run(_run())

    def test_bootstrap_no_windows_raises(self):
        """bootstrap raises RuntimeError when no windows exist."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tmux import bootstrap

            mock_app = MagicMock()
            mock_app.windows = []

            with (
                patch("iterm2.async_get_app", new=AsyncMock(return_value=mock_app)),
                patch(
                    "iterm2.async_get_tmux_connections", new=AsyncMock(return_value=[])
                ),
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    await bootstrap(MagicMock(), timeout=0.1)
                self.assertIn("No iTerm2 windows", str(ctx.exception))

        asyncio.run(_run())
