# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestGetProcessName(unittest.TestCase):
    def test_returns_none_for_none_pid(self):
        from cli_anything.iterm2_ctl.core.session import _get_process_name

        self.assertIsNone(_get_process_name(None))

    def test_returns_process_name_for_real_pid(self):
        """Should return a non-empty string for the current process PID."""
        import os
        from cli_anything.iterm2_ctl.core.session import _get_process_name

        name = _get_process_name(os.getpid())
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)

    def test_returns_none_for_invalid_pid(self):
        from cli_anything.iterm2_ctl.core.session import _get_process_name

        # PID 999999999 almost certainly doesn't exist
        result = _get_process_name(999999999)
        self.assertIsNone(result)

    def test_strips_path_prefix(self):
        """Should return only the basename, not a full path like /usr/bin/python3."""
        from cli_anything.iterm2_ctl.core.session import _get_process_name

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="/usr/bin/python3\n", returncode=0)
            result = _get_process_name(12345)
        self.assertEqual(result, "python3")

    def test_returns_none_on_subprocess_exception(self):
        from cli_anything.iterm2_ctl.core.session import _get_process_name

        with patch("subprocess.run", side_effect=OSError("no ps")):
            result = _get_process_name(12345)
        self.assertIsNone(result)

    def test_handles_string_pid(self):
        """PIDs from iTerm2 variables arrive as strings."""
        from cli_anything.iterm2_ctl.core.session import _get_process_name

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="zsh\n", returncode=0)
            result = _get_process_name("12345")
        self.assertEqual(result, "zsh")
