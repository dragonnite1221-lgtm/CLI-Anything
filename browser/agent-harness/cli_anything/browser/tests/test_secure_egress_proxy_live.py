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
