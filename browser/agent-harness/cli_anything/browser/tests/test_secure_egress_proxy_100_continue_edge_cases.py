"""RFC edge-case regression tests for Expect: 100-continue relaying in the
local pinned egress proxy.

Split out of test_secure_egress_proxy_100_continue.py to keep both files
under the 200-line file-size gate (.github/scripts/check_file_size.py).
"""

from __future__ import annotations

import asyncio

from cli_anything.browser.utils import secure_egress_proxy as proxy


def test_live_http_proxy_relays_early_hints_before_100_continue(monkeypatch):
    """A destination may send other 1xx informational responses (e.g. 103
    Early Hints) before the 100 Continue that actually answers the Expect
    header. Those must be relayed and skipped over, not mistaken for the
    final answer -- otherwise the client's body is never requested and the
    real final response never arrives."""

    async def exercise_proxy():
        async def origin(reader, writer):
            await reader.readuntil(b"\r\n\r\n")
            writer.write(b"HTTP/1.1 103 Early Hints\r\nLink: </style.css>; rel=preload\r\n\r\n")
            await writer.drain()
            writer.write(b"HTTP/1.1 100 Continue\r\n\r\n")
            await writer.drain()
            await reader.readexactly(4)
            writer.write(b"HTTP/1.1 201 Created\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            await writer.drain()
            writer.close()

        origin_server = await asyncio.start_server(origin, "127.0.0.1", 0)
        origin_port = origin_server.sockets[0].getsockname()[1]
        monkeypatch.setattr(proxy, "open_pinned_connection", lambda *_args: asyncio.open_connection("127.0.0.1", origin_port))
        server = await proxy.start_proxy()
        proxy_port = server.sockets[0].getsockname()[1]
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", proxy_port)
            writer.write(
                b"POST http://example.com/upload HTTP/1.1\r\n"
                b"Host: example.com\r\n"
                b"Content-Length: 4\r\n"
                b"Expect: 100-continue\r\n\r\n"
            )
            await writer.drain()

            early_hints = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5)
            interim = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5)

            writer.write(b"test")
            await writer.drain()

            response = await asyncio.wait_for(reader.read(), timeout=5)
            writer.close()
            await writer.wait_closed()
            return early_hints, interim, response
        finally:
            server.close()
            await server.wait_closed()
            origin_server.close()
            await origin_server.wait_closed()

    early_hints, interim, response = asyncio.run(exercise_proxy())

    assert early_hints.startswith(b"HTTP/1.1 103 Early Hints")
    assert interim == b"HTTP/1.1 100 Continue\r\n\r\n"
    assert response.startswith(b"HTTP/1.1 201 Created")


def test_live_http_10_request_with_expect_header_does_not_wait_for_continue(monkeypatch):
    """RFC 9110 10.1.1: a server MUST ignore Expect: 100-continue on an
    HTTP/1.0 request. A destination that correctly ignores it never sends an
    interim response at all -- it goes straight to reading the body. If the
    proxy still waited for one because the client happened to set the
    Expect header, it would deadlock exactly like the bug this relay exists
    to fix, just gated on the request's HTTP version instead of the
    response's status line."""

    async def exercise_proxy():
        async def origin(reader, writer):
            await reader.readuntil(b"\r\n\r\n")
            await reader.readexactly(4)
            writer.write(b"HTTP/1.0 201 Created\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            await writer.drain()
            writer.close()

        origin_server = await asyncio.start_server(origin, "127.0.0.1", 0)
        origin_port = origin_server.sockets[0].getsockname()[1]
        monkeypatch.setattr(proxy, "open_pinned_connection", lambda *_args: asyncio.open_connection("127.0.0.1", origin_port))
        server = await proxy.start_proxy()
        proxy_port = server.sockets[0].getsockname()[1]
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", proxy_port)
            writer.write(
                b"POST http://example.com/upload HTTP/1.0\r\n"
                b"Host: example.com\r\n"
                b"Content-Length: 4\r\n"
                b"Expect: 100-continue\r\n\r\n"
                b"test"
            )
            await writer.drain()

            response = await asyncio.wait_for(reader.read(), timeout=5)
            writer.close()
            await writer.wait_closed()
            return response
        finally:
            server.close()
            await server.wait_closed()
            origin_server.close()
            await origin_server.wait_closed()

    response = asyncio.run(exercise_proxy())

    assert response.startswith(b"HTTP/1.0 201 Created")
