"""Socket relay and process-lifetime mechanics for the secure egress proxy."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import signal

from cli_anything.browser.utils.process_identity import process_identity
from cli_anything.browser.utils.secure_egress_proxy_http import relay_http_request


async def _relay(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while chunk := await reader.read(64 * 1024):
            writer.write(chunk)
            await writer.drain()
    except (ConnectionError, OSError, asyncio.IncompleteReadError):
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except OSError:
            pass


async def relay_both_directions(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    destination_reader: asyncio.StreamReader,
    destination_writer: asyncio.StreamWriter,
) -> None:
    """Relay a CONNECT tunnel or one HTTP request in both directions."""

    await asyncio.gather(
        _relay(client_reader, destination_writer),
        _relay(destination_reader, client_writer),
    )


async def _send_error(writer: asyncio.StreamWriter, status: str) -> None:
    body = b"Secure egress proxy rejected the destination.\n"
    writer.write(
        f"HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n".encode("ascii")
        + body
    )
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def handle_proxy_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    *,
    open_connection,
    parse_authority,
    parse_http_target,
    origin_request_header,
    relay_both_directions,
    rejected_error,
    header_limit: int,
    timeout_seconds: int,
) -> None:
    """Validate and relay one HTTP proxy connection through injected guards."""

    try:
        header = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=timeout_seconds)
        if len(header) > header_limit:
            raise rejected_error("Proxy request header is too large")
        lines = header.decode("iso-8859-1").split("\r\n")
        method, target, version = lines[0].split(" ", 2)
        if version not in {"HTTP/1.0", "HTTP/1.1"}:
            raise rejected_error("Proxy request version is invalid")
        if method.upper() == "CONNECT":
            host, port = parse_authority(target)
            destination_reader, destination_writer = await open_connection(host, port)
            writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await writer.drain()
        else:
            host, port, path = parse_http_target(target)
            destination_reader, destination_writer = await open_connection(host, port)
            headers = lines[1:-2]
            destination_writer.write(origin_request_header(method, path, version, headers))
            await destination_writer.drain()
            await relay_http_request(
                reader,
                writer,
                destination_reader,
                destination_writer,
                headers,
                timeout_seconds,
            )
            return
    except (
        rejected_error,
        ConnectionError,
        UnicodeDecodeError,
        ValueError,
        IndexError,
        asyncio.IncompleteReadError,
        asyncio.LimitOverrunError,
    ):
        await _send_error(writer, "403 Forbidden")
        return
    await relay_both_directions(reader, writer, destination_reader, destination_writer)


def _write_state(path: Path, server: asyncio.AbstractServer) -> None:
    socket_name = server.sockets[0].getsockname()
    identity = process_identity(os.getpid())
    if identity is None:
        raise RuntimeError("secure proxy cannot record a non-reusable process identity")
    payload = json.dumps({"host": socket_name[0], "port": socket_name[1], "pid": os.getpid(), "identity": identity})
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


async def serve_forever(state_file: Path, start_proxy, host: str, port: int) -> None:
    """Run a supplied loopback server factory until SIGINT or SIGTERM."""

    server = await start_proxy(host, port)
    _write_state(state_file, server)
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signum, stopped.set)
        except NotImplementedError:
            signal.signal(signum, lambda *_args: stopped.set())
    try:
        await stopped.wait()
    finally:
        server.close()
        await server.wait_closed()
        try:
            state_file.unlink()
        except FileNotFoundError:
            pass
