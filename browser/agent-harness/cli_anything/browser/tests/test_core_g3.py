# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestDaemonMode:
    """Test daemon mode state propagation."""

    def test_daemon_mode_propagates_to_backend(self):
        """Commands use daemon mode when session.daemon_mode is True."""
        sess = Session()
        sess.enable_daemon()

        with patch("cli_anything.browser.core.fs.backend.ls") as mock_ls:
            mock_ls.return_value = {"path": "/", "entries": []}

            result = fs.list_elements(sess)

            mock_ls.assert_called_once_with("/", use_daemon=True)

    def test_normal_mode_does_not_use_daemon(self):
        """Commands don't use daemon mode when session.daemon_mode is False."""
        sess = Session()
        # daemon_mode defaults to False

        with patch("cli_anything.browser.core.fs.backend.ls") as mock_ls:
            mock_ls.return_value = {"path": "/", "entries": []}

            result = fs.list_elements(sess)

            mock_ls.assert_called_once_with("/", use_daemon=False)
