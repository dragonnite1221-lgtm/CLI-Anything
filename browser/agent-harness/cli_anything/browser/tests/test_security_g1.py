# ruff: noqa: F403, F405, E501
from .test_security_helpers import *  # noqa: F403


class TestPrivateNetworkBlocking:
    """Test private network blocking (controlled by env var)."""

    def test_private_network_blocking_disabled_by_default(self, monkeypatch):
        """By default, private network blocking should be disabled."""
        # Ensure env var is not set
        monkeypatch.delenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", raising=False)
        _reload_security_module()
        assert not is_private_network_blocked()

    def test_localhost_not_blocked_by_default(self, monkeypatch):
        """localhost should not be blocked by default."""
        monkeypatch.delenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", raising=False)
        _reload_security_module()
        is_valid, error = validate_url("http://localhost:3000")
        assert is_valid
        assert error == ""

    def test_127_0_0_1_not_blocked_by_default(self, monkeypatch):
        """127.0.0.1 should not be blocked by default."""
        monkeypatch.delenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", raising=False)
        _reload_security_module()
        is_valid, error = validate_url("http://127.0.0.1:8080")
        assert is_valid
        assert error == ""

    def test_private_network_blocking_enabled(self, monkeypatch):
        """When enabled, localhost should be blocked."""
        monkeypatch.setenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", "true")
        _reload_security_module()
        assert is_private_network_blocked()

        is_valid, error = validate_url("http://localhost:3000")
        assert not is_valid
        assert "blocked" in error.lower()

    def test_127_0_0_1_blocked_when_enabled(self, monkeypatch):
        """When enabled, 127.0.0.1 should be blocked."""
        monkeypatch.setenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", "true")
        _reload_security_module()
        is_valid, error = validate_url("http://127.0.0.1:8080")
        assert not is_valid
        assert "blocked" in error.lower()
