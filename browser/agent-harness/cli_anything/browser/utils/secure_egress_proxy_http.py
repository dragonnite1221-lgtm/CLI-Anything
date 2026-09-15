"""One-request HTTP forwarding for the DNS-pinned loopback proxy."""

from __future__ import annotations

import asyncio

from cli_anything.browser.utils.secure_egress_proxy_continue import (
    CONTINUE_GRACE_SECONDS,
    NoInterimResponse,
    expects_continue,
    relay_interim_response,
)


def _body_framing(headers: list[str]) -> tuple[str, int]:
    lengths: list[int] = []
    encodings: list[str] = []
    for header in headers:
        name, separator, value = header.partition(":")
        if not separator:
            raise ValueError("Proxy request header is malformed")
        if name.lower() == "content-length":
            try:
                lengths.append(int(value.strip(), 10))
            except ValueError as error:
                raise ValueError("Proxy request content length is invalid") from error
        elif name.lower() == "transfer-encoding":
            encodings.append(value.strip().lower())
    if any(length < 0 for length in lengths) or len(set(lengths)) > 1:
        raise ValueError("Proxy request content length is invalid")
    if encodings:
        if lengths or any(encoding != "chunked" for encoding in encodings):
            raise ValueError("Proxy request transfer encoding is unsupported")
        return "chunked", 0
    return "length", lengths[0] if lengths else 0


async def _read_exact(reader: asyncio.StreamReader, size: int, timeout_seconds: int) -> bytes:
    return await asyncio.wait_for(reader.readexactly(size), timeout=timeout_seconds)


async def _forward_chunked_body(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, timeout_seconds: int) -> None:
    while True:
        line = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout_seconds)
        try:
            size = int(line[:-2].split(b";", 1)[0], 16)
        except ValueError as error:
            raise ValueError("Proxy request chunk size is invalid") from error
        if size < 0:
            raise ValueError("Proxy request chunk size is invalid")
        writer.write(line)
        if size:
            chunk = await _read_exact(reader, size + 2, timeout_seconds)
            if not chunk.endswith(b"\r\n"):
                raise ValueError("Proxy request chunk is malformed")
            writer.write(chunk)
            await writer.drain()
            continue
        while True:
            trailer = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout_seconds)
            writer.write(trailer)
            if trailer == b"\r\n":
                await writer.drain()
                return


async def _relay_response(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while chunk := await reader.read(64 * 1024):
            writer.write(chunk)
            await writer.drain()
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            pass


async def relay_http_request(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    destination_reader: asyncio.StreamReader,
    destination_writer: asyncio.StreamWriter,
    headers: list[str],
    timeout_seconds: int,
    version: str = "HTTP/1.1",
) -> None:
    """Forward exactly one framed HTTP request, then close the client connection."""

    try:
        framing, length = _body_framing(headers)
        send_body = True
        # RFC 9110 10.1.1: a server MUST ignore Expect: 100-continue on an
        # HTTP/1.0 request. A destination speaking HTTP/1.0 will never send
        # the interim response, so waiting for one here would deadlock
        # exactly like the bug this relay exists to fix.
        if version == "HTTP/1.1" and expects_continue(headers):
            grace = min(timeout_seconds, CONTINUE_GRACE_SECONDS)
            try:
                send_body = await relay_interim_response(
                    destination_reader, client_writer, grace, timeout_seconds
                )
            except NoInterimResponse:
                # No response started arriving at all within the grace
                # period. RFC 9110 10.1.1 explicitly allows the destination
                # to skip the interim response and read the body directly,
                # so -- like a real client would -- stop waiting and send
                # it. (A stall partway through an already-started response
                # instead raises a plain asyncio.TimeoutError here, which
                # is deliberately NOT caught: the client has already
                # received a partial status line/headers by that point, so
                # papering over it and proceeding to send the body would
                # corrupt the response framing rather than recover it.)
                #
                # Known accepted limitation: once this fires, destination_reader
                # is no longer watched until _relay_response() below. If the
                # destination's 100 Continue lands just after the grace window
                # elapses, it sits unread and gets relayed ahead of the final
                # response once the body finally goes through -- corrupting
                # framing the same way a mid-response stall would, just later.
                # Fully closing this means racing destination-response arrival
                # against client-body arrival (two concurrently awaited reads)
                # instead of committing to one side after the grace period, a
                # meaningfully larger and riskier change for a case that needs
                # an adversarial coincidence of timing to hit in practice
                # (unlike the deadlock this relay fixes, which failed every
                # single time). Left as a follow-up rather than taken on here.
                send_body = True
        if send_body:
            if framing == "chunked":
                await _forward_chunked_body(client_reader, destination_writer, timeout_seconds)
            elif length:
                remaining = length
                while remaining:
                    chunk = await _read_exact(client_reader, min(remaining, 64 * 1024), timeout_seconds)
                    destination_writer.write(chunk)
                    await destination_writer.drain()
                    remaining -= len(chunk)
        # Whether or not a body was sent, the request side of this exchange
        # is finished: a destination that only accepts the request after
        # seeing our half of the stream close must still see that EOF, even
        # when it rejected the body outright.
        if destination_writer.can_write_eof():
            destination_writer.write_eof()
        await destination_writer.drain()
        await _relay_response(destination_reader, client_writer)
    finally:
        destination_writer.close()
        try:
            await destination_writer.wait_closed()
        except OSError:
            pass
