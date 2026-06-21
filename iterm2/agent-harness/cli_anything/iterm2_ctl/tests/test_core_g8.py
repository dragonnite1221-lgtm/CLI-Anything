# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestTabSelectPane(unittest.TestCase):
    def test_invalid_direction_raises(self):
        """select_pane_in_direction raises ValueError for unknown direction."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tab import select_pane_in_direction

            with self.assertRaises(ValueError) as ctx:
                await select_pane_in_direction(MagicMock(), "t1", "diagonal")
            self.assertIn("diagonal", str(ctx.exception))

        asyncio.run(_run())

    def test_valid_direction_calls_api(self):
        """select_pane_in_direction calls async_select_pane_in_direction."""
        import asyncio
        import iterm2
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tab import select_pane_in_direction

            mock_tab = MagicMock()
            mock_tab.tab_id = "t1"
            mock_tab.async_select_pane_in_direction = AsyncMock(return_value="s_new")

            with patch(
                "cli_anything.iterm2_ctl.utils.iterm2_backend.async_find_tab",
                new=AsyncMock(return_value=mock_tab),
            ):
                result = await select_pane_in_direction(MagicMock(), "t1", "right")

            self.assertEqual(result["new_session_id"], "s_new")
            self.assertTrue(result["moved"])

        asyncio.run(_run())

    def test_no_pane_in_direction(self):
        """Returns moved=False when API returns None."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.tab import select_pane_in_direction

            mock_tab = MagicMock()
            mock_tab.tab_id = "t1"
            mock_tab.async_select_pane_in_direction = AsyncMock(return_value=None)

            with patch(
                "cli_anything.iterm2_ctl.utils.iterm2_backend.async_find_tab",
                new=AsyncMock(return_value=mock_tab),
            ):
                result = await select_pane_in_direction(MagicMock(), "t1", "left")

            self.assertFalse(result["moved"])

        asyncio.run(_run())


class TestSessionInjectCLI(unittest.TestCase):
    def test_inject_help(self):
        from click.testing import CliRunner
        from cli_anything.iterm2_ctl.iterm2_ctl_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["session", "inject", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--hex", result.output)

    def test_inject_hex_invalid(self):
        """--hex with invalid hex string exits with error."""
        from click.testing import CliRunner
        from cli_anything.iterm2_ctl.iterm2_ctl_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["session", "inject", "ZZZZ", "--hex"])
        self.assertNotEqual(result.exit_code, 0)


class TestPrefListKeys(unittest.TestCase):
    def test_list_keys_returns_keys(self):
        from click.testing import CliRunner
        from cli_anything.iterm2_ctl.iterm2_ctl_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["pref", "list-keys"])
        self.assertEqual(result.exit_code, 0)
        # Should list something
        self.assertIn("preference key(s)", result.output)

    def test_list_keys_filter(self):
        from click.testing import CliRunner
        from cli_anything.iterm2_ctl.iterm2_ctl_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["pref", "list-keys", "--filter", "TMUX"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("TMUX", result.output)
