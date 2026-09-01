"""A loopback-only HTTP proxy that pins browser egress to validated IPs.

URL validation alone cannot prevent DNS rebinding: a hostname may resolve to a
public address while it is checked and to a private address when Chrome later
opens its own socket.  This proxy owns the latter socket.  It resolves a
destination exactly once, rejects a response containing *any* non-global IP,
and connects Chrome to that selected numeric address rather than the hostname.

It intentionally supports only HTTP proxy requests and HTTPS ``CONNECT``
tunnels.  It listens on loopback and has no authentication because it is a
private companion to a managed browser profile, not a network service.
"""

from __future__ import annotations

import asyncio
import argparse
import ipaddress
import json
import os
from pathlib import Path
import signal
import socket
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlsplit


MAX_REQUEST_HEADER_BYTES = 16 * 1024
CONNECT_TIMEOUT_SECONDS = 15


class DestinationRejected(ConnectionError):
    """Raised when an egress destination is not a globally routable address."""


@dataclass(frozen=True)
class PinnedDestination:
    """The hostname Chrome requested and the numeric address the proxy will use."""

    host: str
    port: int
    address: str


def _normalise_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    address = ipaddress.ip_address(value)
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return address.ipv4_mapped
    return address


def _global_addresses(host: str, port: int) -> tuple[str, ...]:
    """Resolve ``host`` once and return only an all-global address set.

    A mixed DNS answer is rejected instead of selecting the public member.  It
    is an ambiguous security boundary and accepting it would let an attacker
    influence which address a future implementation chooses.
    """

    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, OSError, UnicodeError) as error:
        raise DestinationRejected("Destination hostname could not be resolved") from error

    addresses: list[str] = []
    for info in infos:
        try:
            address = _normalise_ip(info[4][0])
        except ValueError as error:
            raise DestinationRejected("Destination resolver returned an invalid address") from error
        if not address.is_global:
            raise DestinationRejected("Destination resolved to a non-public network address")
        rendered = str(address)
        if rendered not in addresses:
            addresses.append(rendered)

    if not addresses:
        raise DestinationRejected("Destination hostname returned no usable addresses")
    return tuple(addresses)


def resolve_pinned_destination(host: str, port: int) -> PinnedDestination:
    """Validate a destination and select the first resolved numeric address."""

    if not isinstance(host, str) or not host or any(char.isspace() for char in host):
        raise DestinationRejected("Destination hostname is invalid")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise DestinationRejected("Destination port is invalid")
    return PinnedDestination(host=host, port=port, address=_global_addresses(host, port)[0])


async def open_pinned_connection(host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    """Open a TCP connection to the validated numeric address, never a hostname."""

    destination = resolve_pinned_destination(host, port)
    try:
        return await asyncio.wait_for(
            asyncio.open_connection(destination.address, destination.port),
            timeout=CONNECT_TIMEOUT_SECONDS,
        )
    except (OSError, asyncio.TimeoutError) as error:
        raise ConnectionError("Destination connection failed") from error


def _parse_authority(value: str) -> tuple[str, int]:
    """Parse a ``CONNECT host:port`` authority without accepting user-info."""

    if value.startswith("["):
        closing = value.find("]")
        if closing < 0 or not value[closing + 1 :].startswith(":"):
            raise DestinationRejected("CONNECT authority must include a port")
        host = value[1:closing]
        port_text = value[closing + 2 :]
    else:
        host, separator, port_text = value.rpartition(":")
        if not separator:
            raise DestinationRejected("CONNECT authority must include a port")
    if "@" in host:
        raise DestinationRejected("CONNECT authority must not include credentials")
    try:
        port = int(port_text, 10)
    except ValueError as error:
        raise DestinationRejected("CONNECT port is invalid") from error
    if not host or not 1 <= port <= 65535:
        raise DestinationRejected("CONNECT authority is invalid")
    return host, port


def _parse_http_target(target: str) -> tuple[str, int, str]:
    """Return host, port, and origin-form request target for a proxy request."""

    parsed = urlsplit(target)
    if parsed.scheme.lower() != "http" or not parsed.hostname:
        raise DestinationRejected("Proxy request must use an absolute http URL")
    if parsed.username is not None or parsed.password is not None:
        raise DestinationRejected("Proxy request must not include credentials")
    try:
        port = parsed.port or 80
    except ValueError as error:
        raise DestinationRejected("Proxy request port is invalid") from error
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return parsed.hostname, port, path


def _origin_request_header(method: str, path: str, version: str, headers: Iterable[str]) -> bytes:
    """Convert a proxy absolute-form request into an origin-form request."""

    forwarded = [f"{method} {path} {version}"]
    for header in headers:
        name, separator, _value = header.partition(":")
        if not separator:
            raise DestinationRejected("Proxy request header is malformed")
        if name.lower() in {"proxy-connection", "proxy-authorization"}:
            continue
        forwarded.append(header)
    return ("\r\n".join(forwarded) + "\r\n\r\n").encode("iso-8859-1")


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


async def _relay_both_directions(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    destination_reader: asyncio.StreamReader,
    destination_writer: asyncio.StreamWriter,
) -> None:
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


async def handle_proxy_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Process one proxy connection and close it after the request or tunnel ends."""

    try:
        header = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=CONNECT_TIMEOUT_SECONDS)
        if len(header) > MAX_REQUEST_HEADER_BYTES:
            raise DestinationRejected("Proxy request header is too large")
        lines = header.decode("iso-8859-1").split("\r\n")
        method, target, version = lines[0].split(" ", 2)
        if version not in {"HTTP/1.0", "HTTP/1.1"}:
            raise DestinationRejected("Proxy request version is invalid")

        if method.upper() == "CONNECT":
            host, port = _parse_authority(target)
            destination_reader, destination_writer = await open_pinned_connection(host, port)
            writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await writer.drain()
        else:
            host, port, path = _parse_http_target(target)
            destination_reader, destination_writer = await open_pinned_connection(host, port)
            destination_writer.write(_origin_request_header(method, path, version, lines[1:-2]))
            await destination_writer.drain()
    except (
        DestinationRejected,
        ConnectionError,
        UnicodeDecodeError,
        ValueError,
        IndexError,
        asyncio.IncompleteReadError,
    ):
        await _send_error(writer, "403 Forbidden")
        return

    await _relay_both_directions(reader, writer, destination_reader, destination_writer)


async def start_proxy(host: str = "127.0.0.1", port: int = 0) -> asyncio.AbstractServer:
    """Start a loopback-only secure egress proxy and return its server object."""

    if host not in {"127.0.0.1", "::1"}:
        raise ValueError("Secure egress proxy may bind only to loopback")
    return await asyncio.start_server(handle_proxy_client, host=host, port=port, limit=MAX_REQUEST_HEADER_BYTES)


def _write_state(path: Path, server: asyncio.AbstractServer) -> None:
    socket_name = server.sockets[0].getsockname()
    payload = json.dumps({"host": socket_name[0], "port": socket_name[1], "pid": os.getpid()})
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


async def serve_forever(state_file: Path, host: str = "127.0.0.1", port: int = 0) -> None:
    """Run a persistent loopback proxy and publish its private runtime state."""

    server = await start_proxy(host, port)
    _write_state(state_file, server)
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signum, stopped.set)
        except NotImplementedError:  # Windows event loops do not expose signal handlers.
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


def main() -> None:
    """Entrypoint used by the managed-browser runtime supervisor."""

    parser = argparse.ArgumentParser(description="Run the CLI Anything secure egress proxy")
    parser.add_argument("--state-file", required=True, type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=0, type=int)
    arguments = parser.parse_args()
    asyncio.run(serve_forever(arguments.state_file, arguments.host, arguments.port))


if __name__ == "__main__":
    main()
