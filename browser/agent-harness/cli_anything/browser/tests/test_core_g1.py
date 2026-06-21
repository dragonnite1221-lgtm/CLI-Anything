# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestPageModule:
    """Test page command functions."""

    def test_open_page_updates_session(self):
        """Opening a page updates session state."""
        sess = Session()

        with patch("cli_anything.browser.core.page.backend.open_url") as mock_open:
            mock_open.return_value = {"url": "https://example.com", "status": "loaded"}

            result = page.open_page(sess, "https://example.com")

            assert sess.current_url == "https://example.com"
            assert sess.working_dir == "/"  # Reset on new page

    def test_reload_page(self):
        """Reloading page calls backend."""
        sess = Session()
        sess.set_url("https://example.com")

        with patch("cli_anything.browser.core.page.backend.reload") as mock_reload:
            mock_reload.return_value = {"status": "reloaded"}

            result = page.reload_page(sess)
            assert result["status"] == "reloaded"

    def test_go_back_updates_session(self):
        """Going back updates session and calls backend."""
        sess = Session()
        sess.set_url("https://first.com")
        sess.set_url("https://second.com")

        with patch("cli_anything.browser.core.page.backend.back") as mock_back:
            mock_back.return_value = {"url": "https://first.com", "status": "navigated"}

            result = page.go_back(sess)

            assert sess.current_url == "https://first.com"
            assert result["url"] == "https://first.com"

    def test_go_back_empty_history(self):
        """Going back with empty history returns error."""
        sess = Session()

        with patch("cli_anything.browser.core.page.backend.back") as mock_back:
            mock_back.return_value = {"error": "No history"}

            result = page.go_back(sess)
            assert "error" in result

    def test_go_forward_updates_session(self):
        """Going forward updates session and calls backend."""
        sess = Session()
        sess.set_url("https://first.com")
        sess.set_url("https://second.com")
        sess.go_back()  # Now at first.com

        with patch("cli_anything.browser.core.page.backend.forward") as mock_forward:
            mock_forward.return_value = {
                "url": "https://second.com",
                "status": "navigated",
            }

            result = page.go_forward(sess)

            assert sess.current_url == "https://second.com"

    def test_get_page_info(self):
        """Getting page info returns current state."""
        sess = Session()
        sess.set_url("https://example.com")
        sess.set_working_dir("/main")

        result = page.get_page_info(sess)
        assert result["url"] == "https://example.com"
        assert result["working_dir"] == "/main"
