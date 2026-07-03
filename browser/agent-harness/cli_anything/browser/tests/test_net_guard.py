"""SSRF / private-network guard tests (code review M-3).

Covers the ipaddress-based host classification (which the previous regex
matching missed): decimal / hex / IPv4-mapped-IPv6 encodings of private
addresses, plus the default-on blocking behavior and its opt-out.
"""

import importlib

import pytest

from cli_anything.browser.utils._net_guard import host_is_private
from cli_anything.browser.utils import security


def _reload_security():
    importlib.reload(security)


class TestHostIsPrivate:
    @pytest.mark.parametrize(
        "host",
        [
            "127.0.0.1",          # loopback (dotted)
            "2130706433",         # 127.0.0.1 as a decimal integer
            "0x7f000001",         # 127.0.0.1 as hex
            "localhost",          # resolves to loopback
            "::1",                # IPv6 loopback
            "::ffff:127.0.0.1",   # IPv4-mapped IPv6 loopback
            "10.0.0.5",           # RFC1918 class A
            "192.168.1.1",        # RFC1918 class C
            "172.16.0.1",         # RFC1918 class B
            "169.254.169.254",    # link-local (cloud metadata)
            "0.0.0.0",            # unspecified
        ],
    )
    def test_private_encodings_detected(self, host):
        assert host_is_private(host) is True

    @pytest.mark.parametrize("host", ["8.8.8.8", "1.1.1.1"])
    def test_public_ips_allowed(self, host):
        assert host_is_private(host) is False

    def test_unresolvable_host_is_not_private(self):
        # A host we cannot resolve must not be treated as private (fail-open on
        # resolution, but literal private IPs are still always caught).
        assert host_is_private("nonexistent.invalid.") is False


class TestDefaultBlocking:
    def test_private_blocked_by_default(self, monkeypatch):
        monkeypatch.delenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", raising=False)
        monkeypatch.delenv("CLI_ANYTHING_BROWSER_ALLOW_PRIVATE", raising=False)
        _reload_security()
        assert security.is_private_network_blocked() is True
        for url in ("http://127.0.0.1:8080", "http://2130706433/", "http://localhost:3000"):
            is_valid, error = security.validate_url(url)
            assert not is_valid, url
            assert "blocked" in error.lower()

    def test_allow_private_opt_out(self, monkeypatch):
        monkeypatch.setenv("CLI_ANYTHING_BROWSER_ALLOW_PRIVATE", "1")
        _reload_security()
        assert security.is_private_network_blocked() is False
        is_valid, error = security.validate_url("http://127.0.0.1:8080")
        assert is_valid
        assert error == ""

    def test_legacy_block_false_opt_out(self, monkeypatch):
        monkeypatch.setenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", "false")
        monkeypatch.delenv("CLI_ANYTHING_BROWSER_ALLOW_PRIVATE", raising=False)
        _reload_security()
        assert security.is_private_network_blocked() is False


def teardown_module(module):
    # Restore default module state for any later test module that imports it.
    importlib.reload(security)
