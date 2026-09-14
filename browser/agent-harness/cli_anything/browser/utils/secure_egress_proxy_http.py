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
        if separator and name.strip().lower() == "expect" and value.strip().lower() == "100-continue":
            return True
    return False


async def _relay_interim_response(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, timeout_seconds: int
) -> bool:
    """Relay one interim status line + headers from the destination to the client.

    A destination that honors ``Expect: 100-continue`` answers with a "100
    Continue" status line before the client is willing to upload its body.
    That interim response must reach the client immediately -- otherwise the
    client withholds the body waiting for a signal the proxy never forwards,
    while the proxy blocks waiting to read that same body from the client.
    Returns True when the destination signalled 100 Continue (so the body
    should still be uploaded), False when it sent a final status instead (so
    the body must not be sent and this response is the answer to relay).
    """

    status_line = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout_seconds)
    writer.write(status_line)
    while True:
        line = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout_seconds)
        writer.write(line)
        if line == b"\r\n":
            break
    await writer.drain()
    return status_line in (b"HTTP/1.1 100 Continue\r\n", b"HTTP/1.0 100 Continue\r\n")


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
) -> None:
    """Forward exactly one framed HTTP request, then close the client connection."""

    try:
        framing, length = _body_framing(headers)
        send_body = True
        if _expects_continue(headers):
            send_body = await _relay_interim_response(destination_reader, client_writer, timeout_seconds)
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
