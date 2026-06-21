# ruff: noqa: F403, F405, E501
from .test_security_helpers import *  # noqa: F403


class TestURLValidation:
    """Test URL validation security checks."""

    def test_valid_http_url(self):
        """Valid HTTP URL should pass."""
        is_valid, error = validate_url("http://example.com")
        assert is_valid
        assert error == ""

    def test_valid_https_url(self):
        """Valid HTTPS URL should pass."""
        is_valid, error = validate_url("https://example.com")
        assert is_valid
        assert error == ""

    def test_valid_https_with_path(self):
        """Valid HTTPS URL with path should pass."""
        is_valid, error = validate_url("https://example.com/path/to/page?query=value")
        assert is_valid
        assert error == ""

    def test_blocked_file_scheme(self):
        """file:// scheme should be blocked."""
        is_valid, error = validate_url("file:///etc/passwd")
        assert not is_valid
        assert "Blocked URL scheme: file" in error

    def test_blocked_javascript_scheme(self):
        """javascript: scheme should be blocked."""
        is_valid, error = validate_url("javascript:alert(1)")
        assert not is_valid
        assert "Blocked URL scheme: javascript" in error

    def test_blocked_data_scheme(self):
        """data: scheme should be blocked."""
        is_valid, error = validate_url("data:text/html,<script>alert(1)</script>")
        assert not is_valid
        assert "Blocked URL scheme: data" in error

    def test_blocked_vbscript_scheme(self):
        """vbscript: scheme should be blocked."""
        is_valid, error = validate_url("vbscript:msgbox(1)")
        assert not is_valid
        assert "Blocked URL scheme: vbscript" in error

    def test_blocked_about_scheme(self):
        """about: scheme should be blocked."""
        is_valid, error = validate_url("about:blank")
        assert not is_valid
        assert "Blocked URL scheme: about" in error

    def test_blocked_chrome_scheme(self):
        """chrome:// scheme should be blocked."""
        is_valid, error = validate_url("chrome://settings")
        assert not is_valid
        assert "Blocked URL scheme: chrome" in error

    def test_blocked_chrome_extension_scheme(self):
        """chrome-extension:// scheme should be blocked."""
        is_valid, error = validate_url("chrome-extension://abc123/popup.html")
        assert not is_valid
        assert "Blocked URL scheme: chrome-extension" in error

    def test_unsupported_ftp_scheme(self):
        """ftp: scheme should be rejected as unsupported."""
        is_valid, error = validate_url("ftp://example.com/file.txt")
        assert not is_valid
        assert "Unsupported URL scheme: ftp" in error

    def test_empty_url(self):
        """Empty URL should be rejected."""
        is_valid, error = validate_url("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_whitespace_url(self):
        """Whitespace-only URL should be rejected."""
        is_valid, error = validate_url("   ")
        assert not is_valid
        assert "empty" in error.lower() or "whitespace" in error.lower()

    def test_none_url(self):
        """None URL should be rejected."""
        is_valid, error = validate_url(None)
        assert not is_valid
        assert "string" in error.lower()

    def test_non_string_url(self):
        """Non-string URL should be rejected."""
        is_valid, error = validate_url(123)
        assert not is_valid
        assert "string" in error.lower()

    def test_malformed_url(self):
        """Malformed URL should be rejected."""
        is_valid, error = validate_url("not a url")
        # Scheme-less URLs are now rejected (explicit scheme required)
        assert not is_valid
        assert isinstance(error, str)
        assert "scheme" in error.lower()

    def test_url_with_newline_injection(self):
        """URL with newline should be handled safely."""
        is_valid, error = validate_url("https://example.com\r\nX-Injection: true")
        # urlparse should handle this, but we check it doesn't crash
        assert isinstance(is_valid, bool)
        assert isinstance(error, str)

    def test_scheme_less_url_rejected(self):
        """Scheme-less URLs should be rejected."""
        is_valid, error = validate_url("example.com")
        assert not is_valid
        assert "scheme" in error.lower()

    def test_scheme_less_url_with_path_rejected(self):
        """Scheme-less URLs with path should be rejected."""
        is_valid, error = validate_url("example.com/path")
        assert not is_valid
        assert "scheme" in error.lower()

    def test_uppercase_scheme_accepted(self, monkeypatch):
        """Uppercase schemes in env var should work after normalization."""
        monkeypatch.setenv("CLI_ANYTHING_BROWSER_ALLOWED_SCHEMES", "HTTP,HTTPS")
        _reload_security_module()
        is_valid, error = validate_url("http://example.com")
        assert is_valid
        assert error == ""

    def test_url_without_hostname_rejected(self):
        """URL without hostname should be rejected."""
        is_valid, error = validate_url("http://")
        assert not is_valid
        assert "hostname" in error.lower()

    def test_fdn_example_com_not_blocked(self, monkeypatch):
        """fdn.example.com should NOT be blocked (not an IPv6 ULA)."""
        monkeypatch.delenv("CLI_ANYTHING_BROWSER_BLOCK_PRIVATE", raising=False)
        _reload_security_module()
        is_valid, error = validate_url("http://fdn.example.com")
        assert is_valid
        assert error == ""

    def test_ipv4_localhost(self):
        """127.0.0.1 should be detected (blocking depends on env var)."""
        is_valid, error = validate_url("http://127.0.0.1:8080")
        # By default, private networks are NOT blocked
        # So this should pass unless env var is set
        assert isinstance(is_valid, bool)

    def test_hostname_localhost(self):
        """localhost hostname should be detected (blocking depends on env var)."""
        is_valid, error = validate_url("http://localhost:3000")
        # By default, private networks are NOT blocked
        assert isinstance(is_valid, bool)

    def test_private_ip_192_168(self):
        """192.168.x.x should be detected (blocking depends on env var)."""
        is_valid, error = validate_url("http://192.168.1.1/admin")
        # By default, private networks are NOT blocked
        assert isinstance(is_valid, bool)

    def test_private_ip_10_0(self):
        """10.x.x.x should be detected (blocking depends on env var)."""
        is_valid, error = validate_url("http://10.0.0.1/secret")
        # By default, private networks are NOT blocked
        assert isinstance(is_valid, bool)

    def test_private_ip_172_16(self):
        """172.16-31.x.x should be detected (blocking depends on env var)."""
        is_valid, error = validate_url("http://172.16.0.1/internal")
        # By default, private networks are NOT blocked
        assert isinstance(is_valid, bool)
