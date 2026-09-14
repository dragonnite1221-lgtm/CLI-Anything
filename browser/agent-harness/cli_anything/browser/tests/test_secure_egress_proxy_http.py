"""Unit tests for the pure helper functions in secure_egress_proxy_http."""

from __future__ import annotations

from cli_anything.browser.utils.secure_egress_proxy_http import _expects_continue, _status_code


def test_expects_continue_true_for_bare_100_continue():
    assert _expects_continue(["Host: example.com", "Expect: 100-continue"])


def test_expects_continue_true_when_listed_alongside_other_tokens():
    """Expect is a comma-separated list (RFC 9110 10.1.1); 100-continue need
    not be the only or first token."""
    assert _expects_continue(["Expect: foo, 100-continue"])
    assert _expects_continue(["Expect: 100-Continue , bar"])


def test_expects_continue_false_when_absent_or_unrelated():
    assert not _expects_continue(["Host: example.com"])
    assert not _expects_continue(["Expect: foo"])


def test_status_code_parses_regardless_of_reason_phrase():
    assert _status_code(b"HTTP/1.1 100 Continue\r\n") == 100
    assert _status_code(b"HTTP/1.1 100 Go Ahead\r\n") == 100
    assert _status_code(b"HTTP/1.1 201 Created\r\n") == 201


def test_status_code_returns_none_for_malformed_line():
    assert _status_code(b"garbage\r\n") is None
    assert _status_code(b"HTTP/1.1 not-a-number\r\n") is None
