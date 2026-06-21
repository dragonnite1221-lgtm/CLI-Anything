# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestDialogsCore(unittest.TestCase):
    def test_show_alert_calls_api(self):
        """show_alert constructs an Alert and returns button info."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.dialogs import show_alert

            mock_alert_instance = MagicMock()
            mock_alert_instance.async_run = AsyncMock(return_value=1000)

            with patch("iterm2.Alert", return_value=mock_alert_instance):
                result = await show_alert(MagicMock(), "Title", "Sub")
            self.assertEqual(result["button_index"], 1000)
            self.assertEqual(result["button_label"], "OK")

        asyncio.run(_run())

    def test_show_alert_with_buttons(self):
        """show_alert maps button index back to label."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.dialogs import show_alert

            mock_alert_instance = MagicMock()
            mock_alert_instance.async_run = AsyncMock(return_value=1001)

            with patch("iterm2.Alert", return_value=mock_alert_instance):
                result = await show_alert(MagicMock(), "T", "S", buttons=["Yes", "No"])
            self.assertEqual(result["button_index"], 1001)
            self.assertEqual(result["button_label"], "No")

        asyncio.run(_run())

    def test_show_text_input_cancelled(self):
        """show_text_input returns cancelled=True when result is None."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.dialogs import show_text_input

            mock_alert = MagicMock()
            mock_alert.async_run = AsyncMock(return_value=None)

            with patch("iterm2.TextInputAlert", return_value=mock_alert):
                result = await show_text_input(MagicMock(), "T", "S")
            self.assertTrue(result["cancelled"])
            self.assertIsNone(result["text"])

        asyncio.run(_run())

    def test_show_text_input_value(self):
        """show_text_input returns entered text."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.dialogs import show_text_input

            mock_alert = MagicMock()
            mock_alert.async_run = AsyncMock(return_value="hello")

            with patch("iterm2.TextInputAlert", return_value=mock_alert):
                result = await show_text_input(MagicMock(), "T", "S")
            self.assertFalse(result["cancelled"])
            self.assertEqual(result["text"], "hello")

        asyncio.run(_run())

    def test_show_open_panel_cancelled(self):
        """show_open_panel returns cancelled=True when panel is dismissed."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.dialogs import show_open_panel

            mock_panel = MagicMock()
            mock_panel.async_run = AsyncMock(return_value=None)

            with patch("iterm2.OpenPanel", return_value=mock_panel):
                result = await show_open_panel(MagicMock(), "Open")
            self.assertTrue(result["cancelled"])
            self.assertEqual(result["files"], [])

        asyncio.run(_run())

    def test_show_open_panel_files(self):
        """show_open_panel returns chosen files."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            from cli_anything.iterm2_ctl.core.dialogs import show_open_panel

            mock_result = MagicMock()
            mock_result.files = ["/Users/alex/foo.py"]

            mock_panel = MagicMock()
            mock_panel.async_run = AsyncMock(return_value=mock_result)
            mock_panel.options = []

            with patch("iterm2.OpenPanel", return_value=mock_panel):
                result = await show_open_panel(MagicMock(), "Open")
            self.assertFalse(result["cancelled"])
            self.assertEqual(result["files"], ["/Users/alex/foo.py"])

        asyncio.run(_run())
