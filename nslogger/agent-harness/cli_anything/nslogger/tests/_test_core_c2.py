# ruff: noqa: F403, F405, E501
from ._test_core_base import *  # noqa: F403


class _TestNSLoggerListenerMixin2:
    def test_auto_ssl_context_accepts_plaintext_live_packet(self):
        class DummySSLContext:
            def wrap_socket(self, conn, server_side=True):
                raise AssertionError("raw packet should not be TLS-wrapped")

        server, client = __import__("socket").socketpair()
        messages = []
        listener = NSLoggerListener(
            on_message=messages.append,
            use_ssl=True,
            allow_plaintext=True,
        )
        listener._ssl_ctx = DummySSLContext()
        thread = __import__("threading").Thread(
            target=listener._handle_client,
            args=(server, ("127.0.0.1", 50000)),
            daemon=True,
        )

        thread.start()
        client.sendall(encode_message(sequence=43, text="auto raw packet", tag="Network", level=1))
        client.close()
        thread.join(timeout=2.0)

        assert len(messages) == 1
        assert messages[0].sequence == 43
        assert messages[0].text == "auto raw packet"
    def test_handle_client_parses_official_live_packet(self):
        server, client = __import__("socket").socketpair()
        messages = []
        listener = NSLoggerListener(on_message=messages.append)
        thread = __import__("threading").Thread(
            target=listener._handle_client,
            args=(server, ("127.0.0.1", 50000)),
            daemon=True,
        )

        thread.start()
        client.sendall(encode_message(sequence=42, text="live packet", tag="Network", level=1))
        client.close()
        thread.join(timeout=2.0)

        assert len(messages) == 1
        assert messages[0].sequence == 42
        assert messages[0].text == "live packet"
        assert messages[0].tag == "Network"
    def test_handle_client_reports_parse_errors(self):
        server, client = __import__("socket").socketpair()
        errors = []
        listener = NSLoggerListener(on_parse_error=lambda host, port, raw, exc: errors.append((raw, exc)))
        thread = __import__("threading").Thread(
            target=listener._handle_client,
            args=(server, ("127.0.0.1", 50000)),
            daemon=True,
        )

        thread.start()
        client.sendall(struct.pack(">I", 2) + b"\x00\x01")
        client.close()
        thread.join(timeout=2.0)

        assert len(errors) == 1
        assert errors[0][0] == b"\x00\x01"
