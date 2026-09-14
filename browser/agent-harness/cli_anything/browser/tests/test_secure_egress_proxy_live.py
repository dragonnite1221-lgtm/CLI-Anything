"""Socket-level security tests for the local pinned egress proxy."""

from __future__ import annotations

import asyncio

from cli_anything.browser.utils import secure_egress_proxy as proxy


def test_live_http_proxy_closes_after_one_request(monkeypatch):
    async def exercise_proxy():
        received: list[bytes] = []

        async def origin(reader, writer):
            received.append(await reader.read())
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK")
            await writer.drain()
            writer.close()

        origin_server = await asyncio.start_server(origin, "127.0.0.1", 0)
        origin_port = origin_server.sockets[0].getsockname()[1]
        monkeypatch.setattr(proxy, "open_pinned_connection", lambda *_args: asyncio.open_connection("127.0.0.1", origin_port))
        server = await proxy.start_proxy()
        proxy_port = server.sockets[0].getsockname()[1]
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", proxy_port)
            writer.write(b"GET http://first.example/a HTTP/1.1\r\nHost: first.example\r\n\r\nGET http://second.example/b HTTP/1.1\r\nHost: second.example\r\n\r\n")
            await writer.drain()
            response = await reader.read()
            writer.close()
            await writer.wait_closed()
            return received, response
        finally:
            server.close()
            await server.wait_closed()
            origin_server.close()
            await origin_server.wait_closed()

    received, response = asyncio.run(exercise_proxy())

    assert response.endswith(b"OK")
    assert received == [b"GET /a HTTP/1.1\r\nHost: first.example\r\nConnection: close\r\n\r\n"]


def test_live_http_proxy_forwards_a_framed_request_body(monkeypatch):
    async def exercise_proxy():
        received: list[bytes] = []

        async def origin(reader, writer):
            received.append(await reader.read())
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
            writer.write(b"POST http://example.com/upload HTTP/1.1\r\nHost: example.com\r\nContent-Length: 4\r\n\r\ntest")
            await writer.drain()
            response = await reader.read()
            writer.close()
            await writer.wait_closed()
            return received, response
        finally:
            server.close()
            await server.wait_closed()
            origin_server.close()
            await origin_server.wait_closed()

    received, response = asyncio.run(exercise_proxy())

    assert response.startswith(b"HTTP/1.1 201 Created")
    assert received == [b"POST /upload HTTP/1.1\r\nHost: example.com\r\nContent-Length: 4\r\nConnection: close\r\n\r\ntest"]


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


def test_live_proxy_rejects_loopback_and_oversized_headers():
    async def exercise_proxy(request):
        server = await proxy.start_proxy()
        port = server.sockets[0].getsockname()[1]
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            writer.write(request)
            await writer.drain()
            response = await reader.read()
            writer.close()
            await writer.wait_closed()
            return response
        finally:
            server.close()
            await server.wait_closed()

    assert asyncio.run(exercise_proxy(b"CONNECT 127.0.0.1:80 HTTP/1.1\r\nHost: 127.0.0.1:80\r\n\r\n")).startswith(b"HTTP/1.1 403 Forbidden")
    oversized = b"GET http://example.com/ HTTP/1.1\r\nCookie: " + b"x" * proxy.MAX_REQUEST_HEADER_BYTES + b"\r\n\r\n"
    assert asyncio.run(exercise_proxy(oversized)).startswith(b"HTTP/1.1 403 Forbidden")
