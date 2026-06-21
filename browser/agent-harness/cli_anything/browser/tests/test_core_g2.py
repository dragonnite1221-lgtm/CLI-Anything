# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestFsModule:
    """Test filesystem command functions."""

    def test_list_elements(self):
        """Listing elements calls backend with session working_dir."""
        sess = Session()
        sess.set_working_dir("/main")

        with patch("cli_anything.browser.core.fs.backend.ls") as mock_ls:
            mock_ls.return_value = {
                "path": "/main",
                "entries": [
                    {"name": "button", "role": "button", "path": "/main/button[0]"}
                ],
            }

            result = fs.list_elements(sess)

            mock_ls.assert_called_once_with("/main", use_daemon=False)

    def test_list_elements_with_path(self):
        """Listing elements with explicit path overrides working_dir."""
        sess = Session()
        sess.set_working_dir("/main")

        with patch("cli_anything.browser.core.fs.backend.ls") as mock_ls:
            mock_ls.return_value = {"path": "/div", "entries": []}

            result = fs.list_elements(sess, "/div")

            mock_ls.assert_called_once_with("/div", use_daemon=False)

    def test_list_elements_empty_path_uses_working_dir(self):
        """Listing with empty path uses session working_dir."""
        sess = Session()
        sess.set_working_dir("/main")

        with patch("cli_anything.browser.core.fs.backend.ls") as mock_ls:
            mock_ls.return_value = {"path": "/main", "entries": []}

            result = fs.list_elements(sess, "")

            mock_ls.assert_called_once_with("/main", use_daemon=False)

    def test_change_directory_absolute_path(self):
        """Changing to absolute path updates working_dir."""
        sess = Session()

        with patch("cli_anything.browser.core.fs.backend.cd") as mock_cd:
            mock_cd.return_value = {"path": "/main", "status": "changed"}

            result = fs.change_directory(sess, "/main")

            assert sess.working_dir == "/main"
            mock_cd.assert_called_once_with("/main", use_daemon=False)

    def test_change_directory_relative_parent(self):
        """Changing to .. goes up one level."""
        sess = Session()
        sess.set_working_dir("/main/div[0]")

        with patch("cli_anything.browser.core.fs.backend.cd") as mock_cd:
            mock_cd.return_value = {"path": "/main", "status": "changed"}

            result = fs.change_directory(sess, "..")

            assert sess.working_dir == "/main"
            mock_cd.assert_called_once_with("/main", use_daemon=False)

    def test_change_directory_parent_from_root(self):
        """Changing to .. from root stays at root."""
        sess = Session()
        sess.set_working_dir("/")

        with patch("cli_anything.browser.core.fs.backend.cd") as mock_cd:
            result = fs.change_directory(sess, "..")

            assert result["error"] == "Already at root"

    def test_change_directory_current(self):
        """Changing to . stays in same directory."""
        sess = Session()
        sess.set_working_dir("/main")

        with patch("cli_anything.browser.core.fs.backend.cd") as mock_cd:
            mock_cd.return_value = {"path": "/main", "status": "changed"}

            result = fs.change_directory(sess, ".")

            assert sess.working_dir == "/main"

    def test_change_directory_relative_path(self):
        """Changing to relative path appends to working_dir."""
        sess = Session()
        sess.set_working_dir("/main")

        with patch("cli_anything.browser.core.fs.backend.cd") as mock_cd:
            mock_cd.return_value = {"path": "/main/div[0]", "status": "changed"}

            result = fs.change_directory(sess, "div[0]")

            assert sess.working_dir == "/main/div[0]"
            mock_cd.assert_called_once_with("/main/div[0]", use_daemon=False)

    def test_read_element(self):
        """Reading element calls backend."""
        sess = Session()

        with patch("cli_anything.browser.core.fs.backend.cat") as mock_cat:
            mock_cat.return_value = {
                "name": "button",
                "role": "button",
                "text": "Click me",
            }

            result = fs.read_element(sess, "/main/button[0]")

            mock_cat.assert_called_once_with("/main/button[0]", use_daemon=False)

    def test_read_element_empty_path_uses_working_dir(self):
        """Reading with empty path uses session working_dir."""
        sess = Session()
        sess.set_working_dir("/main")

        with patch("cli_anything.browser.core.fs.backend.cat") as mock_cat:
            mock_cat.return_value = {"name": "main", "role": "landmark"}

            result = fs.read_element(sess, "")

            mock_cat.assert_called_once_with("/main", use_daemon=False)

    def test_grep_elements(self):
        """Grepping calls backend with pattern."""
        sess = Session()

        with patch("cli_anything.browser.core.fs.backend.grep") as mock_grep:
            mock_grep.return_value = {"matches": ["/main/button[0]", "/main/link[1]"]}

            result = fs.grep_elements(sess, "Login")

            mock_grep.assert_called_once_with("Login", use_daemon=False)

    def test_grep_elements_with_path(self):
        """Grepping with path cds to that path first, then restores."""
        sess = Session()

        with (
            patch("cli_anything.browser.core.fs.backend.grep") as mock_grep,
            patch("cli_anything.browser.core.fs.backend.cd") as mock_cd,
        ):
            mock_grep.return_value = {"matches": ["/main/button[0]"]}
            mock_cd.return_value = {"path": "/main"}

            result = fs.grep_elements(sess, "Login", "/main")

            mock_grep.assert_called_once_with("Login", use_daemon=False)
            assert mock_cd.call_count == 2
            mock_cd.assert_any_call("/main", use_daemon=False)
            mock_cd.assert_any_call("/", use_daemon=False)
