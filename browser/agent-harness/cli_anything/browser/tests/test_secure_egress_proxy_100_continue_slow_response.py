"""Regression test: a destination that starts an interim response within
the grace period but is merely slow to finish it must not be treated as
if it had gone silent.

Split into its own file (rather than growing
test_secure_egress_proxy_100_continue.py or its edge_cases sibling) to
keep both under the 200-line file-size gate
(.github/scripts/check_file_size.py).
"""

from __future__ import annotations

import asyncio

from cli_anything.browser.utils import secure_egress_proxy as proxy


def test_live_http_proxy_finishes_a_slow_but_already_started_interim_response(monkeypatch):
    """The short grace period only bounds whether a response starts at all
    -- once a status line has begun arriving, the destination has already
    committed to answering the Expect, and finishing that same response's
    headers must use the normal per-request timeout instead. Simulated
    here by having the origin send the 100-Continue status line right
    away, then stall longer than the grace period before finishing the
    blank line that terminates it."""

    async def exercise_proxy():
        async def origin(reader, writer):
            await reader.readuntil(b"\r\n\r\n")
            writer.write(b"HTTP/1.1 100 Continue\r\n")
            await writer.drain()
            # Longer than the ~1s initial grace period, but still well
            # under the proxy's real per-request timeout.
            await asyncio.sleep(1.5)
            writer.write(b"\r\n")
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

    assert interim == b"HTTP/1.1 100 Continue\r\n\r\n"
    assert response.startswith(b"HTTP/1.1 201 Created")


def test_live_http_proxy_finishes_a_status_line_split_across_the_grace_period(monkeypatch):
    """Even a single byte of the status line arriving within the grace
    period means the destination has started responding -- not just a
    status line that arrived complete and whole within that window. A
    partial line like "HTTP/1.1 100 " followed by a pause before the rest
    must be finished with the normal timeout, the same as a complete line
    that merely took its headers slowly to finish."""

    async def exercise_proxy():
        async def origin(reader, writer):
            await reader.readuntil(b"\r\n\r\n")
            writer.write(b"HTTP/1.1 100 ")  # no CRLF yet
            await writer.drain()
            await asyncio.sleep(1.5)  # longer than the ~1s initial grace period
            writer.write(b"Continue\r\n\r\n")
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

    assert interim == b"HTTP/1.1 100 Continue\r\n\r\n"
    assert response.startswith(b"HTTP/1.1 201 Created")
