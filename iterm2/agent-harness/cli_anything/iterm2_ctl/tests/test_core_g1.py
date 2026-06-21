# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestIterm2Backend(unittest.TestCase):
    def test_find_iterm2_app_absent(self):
        from cli_anything.iterm2_ctl.utils.iterm2_backend import find_iterm2_app

        with patch("os.path.isdir", return_value=False):
            with self.assertRaises(RuntimeError) as ctx:
                find_iterm2_app()
            self.assertIn("iTerm2", str(ctx.exception))
            self.assertIn("iterm2.com", str(ctx.exception))

    def test_find_iterm2_app_present(self):
        from cli_anything.iterm2_ctl.utils.iterm2_backend import find_iterm2_app

        with patch("os.path.isdir", return_value=True):
            path = find_iterm2_app()
            self.assertIn("iTerm", path)

    def test_require_iterm2_running_import_error(self):
        from cli_anything.iterm2_ctl.utils.iterm2_backend import require_iterm2_running

        with patch("builtins.__import__", side_effect=ImportError("no module")):
            with self.assertRaises((RuntimeError, ImportError)):
                require_iterm2_running()

    def test_connection_error_help_content(self):
        from cli_anything.iterm2_ctl.utils.iterm2_backend import connection_error_help

        help_text = connection_error_help()
        self.assertIn("iTerm2", help_text)
        self.assertIn("Python API", help_text)
