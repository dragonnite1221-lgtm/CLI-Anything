"""Regression tests for DNS-pinned browser egress."""

from __future__ import annotations

import asyncio
import socket

import pytest

from cli_anything.browser.utils import secure_egress_proxy as proxy


def _answer(*addresses: str):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443)) for address in addresses]


def test_public_destination_is_pinned_to_numeric_address(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: _answer("93.184.216.34"))

    destination = proxy.resolve_pinned_destination("example.com", 443)

    assert destination.host == "example.com"
    assert destination.address == "93.184.216.34"


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.7", "169.254.169.254", "::1"])
def test_non_public_dns_answer_is_rejected(monkeypatch, address):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: _answer(address))

    with pytest.raises(proxy.DestinationRejected, match="non-public"):
        proxy.resolve_pinned_destination("rebind.example", 443)


def test_mixed_dns_answer_is_rejected(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: _answer("93.184.216.34", "127.0.0.1"))

    with pytest.raises(proxy.DestinationRejected, match="non-public"):
        proxy.resolve_pinned_destination("rebind.example", 443)


def test_unresolvable_destination_is_rejected(monkeypatch):
    def fail(*_args, **_kwargs):
        raise socket.gaierror("not found")

    monkeypatch.setattr(socket, "getaddrinfo", fail)

    with pytest.raises(proxy.DestinationRejected, match="could not be resolved"):
        proxy.resolve_pinned_destination("missing.invalid", 443)


def test_pinned_connection_uses_numeric_address(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: _answer("93.184.216.34"))
    seen: list[tuple[str, int]] = []

    async def fake_open_connection(host, port):
        seen.append((host, port))
        return object(), object()

    monkeypatch.setattr(proxy.asyncio, "open_connection", fake_open_connection)

    asyncio.run(proxy.open_pinned_connection("example.com", 443))

    assert seen == [("93.184.216.34", 443)]


def test_pinned_connection_tries_each_validated_address(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: _answer("2001:4860:4860::8888", "93.184.216.34"))
    seen: list[tuple[str, int]] = []

    async def fake_open_connection(host, port):
        seen.append((host, port))
        if host == "2001:4860:4860::8888":
            raise OSError("IPv6 route unavailable")
        return object(), object()

    monkeypatch.setattr(proxy.asyncio, "open_connection", fake_open_connection)

    asyncio.run(proxy.open_pinned_connection("example.com", 443))

    assert seen == [("2001:4860:4860::8888", 443), ("93.184.216.34", 443)]


def test_connect_authority_requires_safe_host_and_port():
    assert proxy._parse_authority("example.com:443") == ("example.com", 443)
    assert proxy._parse_authority("[2001:db8::1]:8443") == ("2001:db8::1", 8443)

    with pytest.raises(proxy.DestinationRejected):
        proxy._parse_authority("user@example.com:443")


def test_http_proxy_target_is_converted_to_origin_form():
    host, port, path = proxy._parse_http_target("http://example.com:8080/a?b=c")

    assert (host, port, path) == ("example.com", 8080, "/a?b=c")
    assert proxy._origin_request_header(
        "GET", path, "HTTP/1.1", ["Host: example.com", "Proxy-Connection: keep-alive"]
    ) == b"GET /a?b=c HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"


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
            writer.write(
                b"GET http://first.example/a HTTP/1.1\r\nHost: first.example\r\n\r\n"
                b"GET http://second.example/b HTTP/1.1\r\nHost: second.example\r\n\r\n"
            )
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


def test_live_proxy_rejects_loopback_connect():
    async def exercise_proxy():
        server = await proxy.start_proxy()
        port = server.sockets[0].getsockname()[1]
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            writer.write(b"CONNECT 127.0.0.1:80 HTTP/1.1\r\nHost: 127.0.0.1:80\r\n\r\n")
            await writer.drain()
            response = await reader.read()
            writer.close()
            await writer.wait_closed()
            return response
        finally:
            server.close()
            await server.wait_closed()

    assert asyncio.run(exercise_proxy()).startswith(b"HTTP/1.1 403 Forbidden")
