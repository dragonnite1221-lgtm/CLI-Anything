# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


class TestSession:
    """Test Session state management."""

    def test_session_initial_state(self):
        """Session starts with empty state."""
        sess = Session()
        assert sess.current_url == ""
        assert sess.working_dir == "/"
        assert sess.history == []
        assert sess.forward_stack == []
        assert not sess.daemon_mode

    def test_set_url(self):
        """Setting URL updates state and records history."""
        sess = Session()
        sess.set_url("https://example.com")
        assert sess.current_url == "https://example.com"
        assert sess.history == []

    def test_set_url_with_history(self):
        """Setting URL with history=True records previous URL."""
        sess = Session()
        sess.set_url("https://first.com")
        sess.set_url("https://second.com")
        assert sess.history == ["https://first.com"]
        assert sess.current_url == "https://second.com"

    def test_set_url_clears_forward_stack(self):
        """Setting URL clears forward stack."""
        sess = Session()
        sess.set_url("https://first.com")
        sess.set_url("https://second.com", record_history=True)
        sess.go_back()
        sess.set_url("https://third.com")
        assert sess.forward_stack == []

    def test_go_back(self):
        """Going back pops from history and pushes to forward stack."""
        sess = Session()
        sess.set_url("https://first.com")
        sess.set_url("https://second.com")
        sess.set_url("https://third.com")

        previous = sess.go_back()
        assert previous == "https://second.com"
        assert sess.current_url == "https://second.com"
        assert sess.history == ["https://first.com"]
        assert sess.forward_stack == ["https://third.com"]

    def test_go_back_empty_history(self):
        """Going back with empty history returns None."""
        sess = Session()
        result = sess.go_back()
        assert result is None

    def test_go_forward(self):
        """Going forward pops from forward stack and pushes to history."""
        sess = Session()
        sess.set_url("https://first.com")
        sess.set_url("https://second.com")
        sess.go_back()
        sess.go_back()  # Now at first.com

        next_url = sess.go_forward()
        assert next_url == "https://second.com"
        assert sess.current_url == "https://second.com"
        assert sess.history == ["https://first.com"]
        assert sess.forward_stack == []

    def test_go_forward_empty_stack(self):
        """Going forward with empty stack returns None."""
        sess = Session()
        result = sess.go_forward()
        assert result is None

    def test_set_working_dir(self):
        """Setting working dir updates state."""
        sess = Session()
        sess.set_working_dir("/main/div[0]")
        assert sess.working_dir == "/main/div[0]"

    def test_daemon_mode(self):
        """Daemon mode flag can be toggled."""
        sess = Session()
        assert not sess.daemon_mode

        sess.enable_daemon()
        assert sess.daemon_mode

        sess.disable_daemon()
        assert not sess.daemon_mode

    def test_status(self):
        """Status returns current state as dict."""
        sess = Session()
        sess.set_url("https://example.com")
        sess.set_working_dir("/main")

        status = sess.status()
        assert status["current_url"] == "https://example.com"
        assert status["working_dir"] == "/main"
        assert status["history_length"] == 0
        assert status["forward_stack_length"] == 0
        assert not status["daemon_mode"]
