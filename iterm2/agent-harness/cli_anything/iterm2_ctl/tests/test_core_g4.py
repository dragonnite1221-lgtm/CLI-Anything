# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestBroadcastCore(unittest.TestCase):
    """Unit tests for core/broadcast.py."""

    def test_get_broadcast_domains_empty(self):
        """get_broadcast_domains returns empty list when no domains active."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.broadcast import get_broadcast_domains

            mock_app = MagicMock()
            mock_app.async_refresh_broadcast_domains = AsyncMock()
            mock_app.broadcast_domains = []

            with patch(
                "iterm2.async_get_app",
                new=AsyncMock(return_value=mock_app),
            ):
                result = await get_broadcast_domains(MagicMock())
                self.assertEqual(result, [])

        asyncio.run(_run())

    def test_clear_broadcast_calls_set(self):
        """clear_broadcast calls async_set_broadcast_domains with empty list."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.broadcast import clear_broadcast

            with patch(
                "iterm2.async_set_broadcast_domains",
                new=AsyncMock(),
            ) as mock_set:
                result = await clear_broadcast(MagicMock())
                mock_set.assert_awaited_once()
                self.assertEqual(result["domains"], [])
                self.assertTrue(result["cleared"])

        asyncio.run(_run())


class TestMenuCore(unittest.TestCase):
    """Unit tests for core/menu.py."""

    def test_list_common_menu_items_structure(self):
        """list_common_menu_items returns list of dicts with identifier+description."""
        import asyncio

        async def _run():
            from cli_anything.iterm2_ctl.core.menu import list_common_menu_items

            result = await list_common_menu_items(MagicMock())
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
            for item in result:
                self.assertIn("identifier", item)
                self.assertIn("description", item)

        asyncio.run(_run())

    def test_select_menu_item_calls_api(self):
        """select_menu_item calls MainMenu.async_select_menu_item."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.menu import select_menu_item

            with patch(
                "iterm2.MainMenu.async_select_menu_item",
                new=AsyncMock(),
            ) as mock_select:
                result = await select_menu_item(MagicMock(), "Shell/New Window")
                mock_select.assert_awaited_once()
                self.assertTrue(result["invoked"])
                self.assertEqual(result["identifier"], "Shell/New Window")

        asyncio.run(_run())


class TestPrefCore(unittest.TestCase):
    """Unit tests for core/pref.py."""

    def test_parse_value_bool_true(self):
        from cli_anything.iterm2_ctl.core.pref import _parse_value

        self.assertTrue(_parse_value("true"))
        self.assertTrue(_parse_value("True"))
        self.assertTrue(_parse_value("TRUE"))

    def test_parse_value_bool_false(self):
        from cli_anything.iterm2_ctl.core.pref import _parse_value

        self.assertFalse(_parse_value("false"))

    def test_parse_value_int(self):
        from cli_anything.iterm2_ctl.core.pref import _parse_value

        self.assertEqual(_parse_value("42"), 42)
        self.assertIsInstance(_parse_value("42"), int)

    def test_parse_value_float(self):
        from cli_anything.iterm2_ctl.core.pref import _parse_value

        self.assertAlmostEqual(_parse_value("3.14"), 3.14)

    def test_parse_value_string(self):
        from cli_anything.iterm2_ctl.core.pref import _parse_value

        self.assertEqual(_parse_value("hello"), "hello")

    def test_parse_value_passthrough_non_string(self):
        from cli_anything.iterm2_ctl.core.pref import _parse_value

        self.assertEqual(_parse_value(42), 42)

    def test_set_tmux_preference_unknown_setting(self):
        """set_tmux_preference raises ValueError for unknown setting name."""
        import asyncio

        async def _run():
            from cli_anything.iterm2_ctl.core.pref import set_tmux_preference

            with self.assertRaises(ValueError) as ctx:
                await set_tmux_preference(MagicMock(), "nonexistent_setting", "1")
            self.assertIn("nonexistent_setting", str(ctx.exception))

        asyncio.run(_run())
