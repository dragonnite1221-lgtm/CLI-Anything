# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestNSLoggerListenerMixin1:
    def test_ssl_handshake_failure_is_silent(self):
        class DummySSLContext:
            def wrap_socket(self, conn, server_side=True):
                raise OSError(22, "Invalid argument")

        class DummyConn:
            def __init__(self):
                self.closed = False
                self.peeked = False

            def recv(self, n, flags=0):
                if flags:
                    self.peeked = True
                    return b"\x16\x03\x01\x00\x2a"
                return b""

            def settimeout(self, timeout):
                pass

            def close(self):
                self.closed = True

        connect_calls = []
        disconnect_calls = []

        listener = NSLoggerListener(
            on_connect=lambda host, port: connect_calls.append((host, port)),
            on_disconnect=lambda host, port: disconnect_calls.append((host, port)),
        )
        listener._ssl_ctx = DummySSLContext()
        conn = DummyConn()

        listener._handle_client(conn, ("127.0.0.1", 50000))

        assert conn.closed is True
        assert connect_calls == []
        assert disconnect_calls == []
    def test_raw_connection_without_ssl_context_is_not_wrapped(self):
        class DummyConn:
            def __init__(self, payload: bytes):
                self.payload = payload
                self.closed = False

            def recv(self, n, flags=0):
                if flags == getattr(__import__("socket"), "MSG_PEEK", 0):
                    return self.payload[:n]
                return b""

            def settimeout(self, timeout):
                pass

            def close(self):
                self.closed = True

        listener = NSLoggerListener(use_ssl=False)
        conn = DummyConn(b"\x00\x00\x00\x10\x00")

        assert _looks_like_tls_client_hello(conn) is False
        listener._handle_client(conn, ("127.0.0.1", 50000))
        assert conn.closed is True
    def test_tls_client_hello_is_detected(self):
        class DummyConn:
            def recv(self, n, flags=0):
                if flags == getattr(__import__("socket"), "MSG_PEEK", 0):
                    return b"\x16\x03\x01\x00\x2a"
                return b""

        assert _looks_like_tls_client_hello(DummyConn()) is True
    def test_connection_classifier_distinguishes_tls_raw_and_empty(self):
        class DummyConn:
            def __init__(self, payload: bytes):
                self.payload = payload

            def recv(self, n, flags=0):
                return self.payload[:n]

        assert _classify_connection(DummyConn(b"\x16\x03\x01\x00\x2a"))[0] == "tls"
        assert _classify_connection(DummyConn(b"\x00\x00\x00\x10\x00"))[0] == "raw"
        assert _classify_connection(DummyConn(b""))[0] == "empty"
    def test_connection_classifier_distinguishes_timeout_from_empty_probe(self):
        class DummyConn:
            def recv(self, n, flags=0):
                raise __import__("socket").timeout()

        assert _classify_connection(DummyConn())[0] == "timeout"
