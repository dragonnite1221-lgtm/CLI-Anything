# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestCLIHelp(unittest.TestCase):
    """Verify CLI structure without requiring iTerm2 connection."""

    def _invoke(self, args):
        from click.testing import CliRunner
        from cli_anything.iterm2_ctl.iterm2_ctl_cli import cli

        runner = CliRunner()
        return runner.invoke(cli, args)

    def test_main_help(self):
        result = self._invoke(["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("iterm2", result.output.lower())

    def test_app_help(self):
        result = self._invoke(["app", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("status", result.output)

    def test_window_help(self):
        result = self._invoke(["window", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("create", result.output)
        self.assertIn("list", result.output)

    def test_tab_help(self):
        result = self._invoke(["tab", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("create", result.output)

    def test_session_help(self):
        result = self._invoke(["session", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("send", result.output)
        self.assertIn("screen", result.output)

    def test_profile_help(self):
        result = self._invoke(["profile", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("list", result.output)

    def test_arrangement_help(self):
        result = self._invoke(["arrangement", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("save", result.output)
        self.assertIn("restore", result.output)

    def test_json_flag_in_help(self):
        result = self._invoke(["--help"])
        self.assertIn("json", result.output.lower())

    def test_session_send_help(self):
        result = self._invoke(["session", "send", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("text", result.output.lower())

    def test_session_split_help(self):
        result = self._invoke(["session", "split", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("vertical", result.output.lower())

    def test_tmux_help(self):
        result = self._invoke(["tmux", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("list", result.output)
        self.assertIn("send", result.output)

    def test_tmux_list_help(self):
        result = self._invoke(["tmux", "list", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_tmux_send_help(self):
        result = self._invoke(["tmux", "send", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("command", result.output.lower())

    def test_tmux_create_window_help(self):
        result = self._invoke(["tmux", "create-window", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_tmux_set_visible_help(self):
        result = self._invoke(["tmux", "set-visible", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("on", result.output)
        self.assertIn("off", result.output)

    def test_tmux_tabs_help(self):
        result = self._invoke(["tmux", "tabs", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_session_run_tmux_cmd_help(self):
        result = self._invoke(["session", "run-tmux-cmd", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("command", result.output.lower())

    def test_session_get_prompt_help(self):
        result = self._invoke(["session", "get-prompt", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_session_wait_prompt_help(self):
        result = self._invoke(["session", "wait-prompt", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("timeout", result.output.lower())

    def test_session_wait_command_end_help(self):
        result = self._invoke(["session", "wait-command-end", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_app_get_var_help(self):
        result = self._invoke(["app", "get-var", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_app_set_var_help(self):
        result = self._invoke(["app", "set-var", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_broadcast_help(self):
        result = self._invoke(["broadcast", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("list", result.output)
        self.assertIn("clear", result.output)

    def test_broadcast_list_help(self):
        result = self._invoke(["broadcast", "list", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_broadcast_set_help(self):
        result = self._invoke(["broadcast", "set", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_broadcast_add_help(self):
        result = self._invoke(["broadcast", "add", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_broadcast_all_panes_help(self):
        result = self._invoke(["broadcast", "all-panes", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_menu_help(self):
        result = self._invoke(["menu", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("select", result.output)
        self.assertIn("list-common", result.output)

    def test_menu_select_help(self):
        result = self._invoke(["menu", "select", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("identifier", result.output.lower())

    def test_menu_list_common_help(self):
        result = self._invoke(["menu", "list-common", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_pref_help(self):
        result = self._invoke(["pref", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("get", result.output)
        self.assertIn("set", result.output)
        self.assertIn("tmux-get", result.output)

    def test_pref_get_help(self):
        result = self._invoke(["pref", "get", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_pref_tmux_get_help(self):
        result = self._invoke(["pref", "tmux-get", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_pref_tmux_set_help(self):
        result = self._invoke(["pref", "tmux-set", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("open_in", result.output)

    def test_pref_theme_help(self):
        result = self._invoke(["pref", "theme", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_tmux_bootstrap_help(self):
        result = self._invoke(["tmux", "bootstrap", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("attach", result.output.lower())
