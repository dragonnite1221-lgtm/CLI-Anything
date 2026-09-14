"""Socket-level regression tests for Expect: 100-continue relaying in the
local pinned egress proxy.

Split out of test_secure_egress_proxy_live.py to keep that file under the
200-line file-size gate (.github/scripts/check_file_size.py).
"""

from __future__ import annotations

import asyncio

from cli_anything.browser.utils import secure_egress_proxy as proxy


def test_live_http_proxy_relays_100_continue_before_body(monkeypatch):
    """The proxy must relay an interim 100-Continue response before the
    client's request body has finished uploading, or an Expect:
    100-continue client and the destination server deadlock: the client
    withholds its body until it sees 100 Continue, but the proxy blocks
    reading the body from the client before it ever looks at the
    destination's response stream.
    """

    async def exercise_proxy():
        received: list[bytes] = []

        async def origin(reader, writer):
            header = await reader.readuntil(b"\r\n\r\n")
            writer.write(b"HTTP/1.1 100 Continue\r\n\r\n")
            await writer.drain()
            body = await reader.readexactly(4)
            received.append(header + body)
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

            # A well-behaved 100-continue client waits for the interim
            # response before uploading the body. If the proxy never
            # relays it, this hangs until the timeout fires.
            interim = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5)

            writer.write(b"test")
            await writer.drain()

            response = await asyncio.wait_for(reader.read(), timeout=5)
            writer.close()
            await writer.wait_closed()
            return interim, received, response
        finally:
            server.close()
            await server.wait_closed()
            origin_server.close()
            await origin_server.wait_closed()

    interim, received, response = asyncio.run(exercise_proxy())

    assert interim == b"HTTP/1.1 100 Continue\r\n\r\n"
    assert response.startswith(b"HTTP/1.1 201 Created")
    assert received == [
        b"POST /upload HTTP/1.1\r\nHost: example.com\r\nContent-Length: 4\r\nExpect: 100-continue\r\nConnection: close\r\n\r\ntest"
    ]


def test_live_http_proxy_relays_100_continue_with_nonstandard_reason_phrase(monkeypatch):
    """RFC 9112 section 4: the reason phrase is free-form and not
    semantically meaningful -- only the three-digit status code says
    whether this is the 100-Continue signal. A destination replying "100 Go
    Ahead" instead of the conventional "100 Continue" must still unblock the
    client's body upload."""

    async def exercise_proxy():
        async def origin(reader, writer):
            await reader.readuntil(b"\r\n\r\n")
            writer.write(b"HTTP/1.1 100 Go Ahead\r\n\r\n")
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

            interim = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5)

            writer.write(b"test")
            await writer.drain()

            response = await asyncio.wait_for(reader.read(), timeout=5)
            writer.close()
            await writer.wait_closed()
            return interim, response
        finally:
            server.close()
            await server.wait_closed()
            origin_server.close()
            await origin_server.wait_closed()

    interim, response = asyncio.run(exercise_proxy())

    assert interim == b"HTTP/1.1 100 Go Ahead\r\n\r\n"
    assert response.startswith(b"HTTP/1.1 201 Created")

