"""One-request HTTP forwarding for the DNS-pinned loopback proxy."""

from __future__ import annotations

import asyncio


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


def _expects_continue(headers: list[str]) -> bool:
    for header in headers:
        name, separator, value = header.partition(":")
        if not separator or name.strip().lower() != "expect":
            continue
        # Expect is a comma-separated list (RFC 9110 10.1.1); "100-continue"
        # is the only expectation defined, but it need not stand alone.
        tokens = [token.strip().lower() for token in value.split(",")]
        if "100-continue" in tokens:
            return True
    return False


def _status_code(status_line: bytes) -> int | None:
    parts = status_line.split(b" ", 2)
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


# RFC 9110 10.1.1 permits a destination to omit the 100-Continue response
# entirely and just read the request body directly -- there is no way to
# tell "not sending one" apart from "about to send one" except by waiting.
# The same section tells *clients* not to wait indefinitely for exactly
# this reason. Mirror that with a short, bounded grace period instead of
# the full per-operation timeout, so a destination that silently proceeds
# doesn't deadlock this relay for the whole connection timeout.
_CONTINUE_GRACE_SECONDS = 1


async def _relay_interim_response(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, timeout_seconds: int
) -> bool:
    """Relay interim (1xx) responses from the destination to the client,
    stopping at the first 100 Continue or first final (non-1xx) status.

    A destination that honors ``Expect: 100-continue`` answers with a "100
    Continue" status line before the client is willing to upload its body.
    That interim response must reach the client immediately -- otherwise the
    client withholds the body waiting for a signal the proxy never forwards,
    while the proxy blocks waiting to read that same body from the client.
    A compliant destination may also send other 1xx responses first (e.g.
    103 Early Hints) before 100 Continue; those must be relayed and skipped
    over rather than mistaken for the final answer. The status code -- not
    the free-form reason phrase -- decides how to proceed. Returns True once
    100 Continue is seen (the body should still be uploaded), False once a
    final status is seen instead (the body must not be sent and this
    response is the answer to relay).
    """

    while True:
        status_line = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout_seconds)
        writer.write(status_line)
        await writer.drain()
        while True:
            line = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout_seconds)
            writer.write(line)
            await writer.drain()
            if line == b"\r\n":
                break
        status = _status_code(status_line)
        if status == 100:
            return True
        if status is None or status >= 200:
            return False
        # Other 1xx informational response (e.g. 103 Early Hints): keep
        # reading for the response that actually answers the Expect.


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
        if version == "HTTP/1.1" and _expects_continue(headers):
            grace = min(timeout_seconds, _CONTINUE_GRACE_SECONDS)
            try:
                send_body = await _relay_interim_response(destination_reader, client_writer, grace)
            except asyncio.TimeoutError:
                # The destination hasn't answered the Expect within the
                # grace period. RFC 9110 10.1.1 explicitly allows it to
                # skip the interim response and read the body directly, so
                # -- like a real client would -- stop waiting and send it.
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
