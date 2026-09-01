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
    ) == b"GET /a?b=c HTTP/1.1\r\nHost: example.com\r\n\r\n"


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
