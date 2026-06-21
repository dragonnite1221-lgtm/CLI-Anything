# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestNewCommandHelp(unittest.TestCase):
    """Smoke-test --help for every new command added in the refine pass."""

    def _help(self, *args):
        from click.testing import CliRunner
        from cli_anything.iterm2_ctl.iterm2_ctl_cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, list(args) + ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)
        return result.output

    def test_app_alert_help(self):
        out = self._help("app", "alert")
        self.assertIn("modal alert", out.lower())

    def test_app_text_input_help(self):
        out = self._help("app", "text-input")
        self.assertIn("text input", out.lower())

    def test_app_file_panel_help(self):
        out = self._help("app", "file-panel")
        self.assertIn("open file panel", out.lower())

    def test_app_save_panel_help(self):
        out = self._help("app", "save-panel")
        self.assertIn("save file panel", out.lower())

    def test_session_inject_help(self):
        out = self._help("session", "inject")
        self.assertIn("inject", out.lower())
        self.assertIn("hex", out.lower())

    def test_tab_select_pane_help(self):
        out = self._help("tab", "select-pane")
        self.assertIn("direction", out.lower())

    def test_profile_get_help(self):
        out = self._help("profile", "get")
        self.assertIn("guid", out.lower())

    def test_pref_list_keys_help(self):
        out = self._help("pref", "list-keys")
        self.assertIn("preference", out.lower())
