"""Zoom OAuth CSRF-state + reflected-XSS hardening tests (code review M-4)."""

import threading
import time
import urllib.error
import urllib.request

import pytest

from cli_anything.zoom.core import _oauth_callback
from cli_anything.zoom.core._oauth_callback import capture_oauth_callback
from cli_anything.zoom.utils.zoom_backend import get_authorize_url


class TestAuthorizeUrlState:
    def test_state_included_when_given(self):
        url = get_authorize_url("cid", "http://localhost:4199/callback", state="tok123")
        assert "state=tok123" in url

    def test_state_omitted_by_default(self):
        url = get_authorize_url("cid", "http://localhost:4199/callback")
        assert "state=" not in url


def _drive_callback(monkeypatch, port, query, expected_state="good-state"):
    """Run capture_oauth_callback in a thread and hit it once with ?query."""
    monkeypatch.setattr(_oauth_callback.webbrowser, "open", lambda url: None)
    out = {}

    def target():
        out["result"] = capture_oauth_callback(
            "http://unused", port, expected_state=expected_state, timeout=5
        )

    thread = threading.Thread(target=target)
    thread.start()
    body = None
    for _ in range(50):  # wait for the server to bind, then send one request
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/callback?{query}") as resp:
                body = resp.read().decode()
            break
        except urllib.error.HTTPError as exc:  # 400 responses still carry a body
            body = exc.read().decode()
            break
        except urllib.error.URLError:
            time.sleep(0.05)
    thread.join(5)
    return out.get("result"), body


class TestCallbackStateValidation:
    def test_matching_state_returns_code(self, monkeypatch):
        (code, error), body = _drive_callback(monkeypatch, 4271, "code=abc&state=good-state")
        assert code == "abc"
        assert error is None
        assert "successful" in body.lower()

    def test_mismatched_state_rejected(self, monkeypatch):
        (code, error), body = _drive_callback(monkeypatch, 4272, "code=abc&state=attacker")
        assert code is None
        assert error is not None and "state" in error.lower()

    def test_missing_state_rejected(self, monkeypatch):
        (code, error), _ = _drive_callback(monkeypatch, 4273, "code=abc")
        assert code is None
        assert error is not None

    def test_error_description_is_html_escaped(self, monkeypatch):
        payload = "error=access_denied&error_description=%3Cscript%3Ealert(1)%3C/script%3E&state=good-state"
        (code, error), body = _drive_callback(monkeypatch, 4274, payload)
        assert code is None
        assert "<script>" not in body           # raw tag must not be reflected
        assert "&lt;script&gt;" in body          # it is HTML-escaped instead


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
