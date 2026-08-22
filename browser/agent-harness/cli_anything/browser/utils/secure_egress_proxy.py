"""Loopback-only proxy admission checks with DNS-pinned destination selection."""

from __future__ import annotations

import argparse
import asyncio
import ipaddress
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit

from cli_anything.browser.utils import secure_egress_proxy_server as _server


MAX_REQUEST_HEADER_BYTES = 16 * 1024
CONNECT_TIMEOUT_SECONDS = 15


class DestinationRejected(ConnectionError):
    """Raised when a destination is not globally routable."""


@dataclass(frozen=True)
class PinnedDestination:
    """The requested hostname and its validated numeric connection addresses."""

    host: str
    port: int
    addresses: tuple[str, ...]

    @property
    def address(self) -> str:
        """Retain the primary-address API for callers that only need inspection."""

        return self.addresses[0]


def _normalise_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    address = ipaddress.ip_address(value)
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return address.ipv4_mapped
    return address


def _global_addresses(host: str, port: int) -> tuple[str, ...]:
    """Resolve once and reject a response containing any non-global address."""

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
    """Validate a destination and retain every resolved numeric address."""

    if not isinstance(host, str) or not host or any(char.isspace() for char in host):
        raise DestinationRejected("Destination hostname is invalid")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise DestinationRejected("Destination port is invalid")
    return PinnedDestination(host=host, port=port, addresses=_global_addresses(host, port))


async def open_pinned_connection(host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    """Connect to the validated numeric address, never a caller-controlled hostname."""

    destination = resolve_pinned_destination(host, port)
    for address in destination.addresses:
        try:
            return await asyncio.wait_for(
                asyncio.open_connection(address, destination.port),
                timeout=CONNECT_TIMEOUT_SECONDS,
            )
        except (OSError, asyncio.TimeoutError):
            continue
    raise ConnectionError("Destination connection failed")


def _parse_authority(value: str) -> tuple[str, int]:
    """Parse a CONNECT authority without accepting user-info."""

    if value.startswith("["):
        closing = value.find("]")
        if closing < 0 or not value[closing + 1 :].startswith(":"):
            raise DestinationRejected("CONNECT authority must include a port")
        host, port_text = value[1:closing], value[closing + 2 :]
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
    """Return host, port, and origin-form target for an HTTP proxy request."""

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
    return parsed.hostname, port, f"{path}?{parsed.query}" if parsed.query else path


def _origin_request_header(method: str, path: str, version: str, headers: Iterable[str]) -> bytes:
    """Convert an absolute-form proxy request to an origin-form request."""

    forwarded = [f"{method} {path} {version}"]
    for header in headers:
        name, separator, _value = header.partition(":")
        if not separator:
            raise DestinationRejected("Proxy request header is malformed")
        if name.lower() not in {"connection", "proxy-connection", "proxy-authorization"}:
            forwarded.append(header)
    forwarded.append("Connection: close")
    return ("\r\n".join(forwarded) + "\r\n\r\n").encode("iso-8859-1")


_relay_both_directions = _server.relay_both_directions


async def handle_proxy_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Handle one proxy client while retaining injectable facade dependencies."""

    await _server.handle_proxy_client(
        reader,
        writer,
        open_connection=open_pinned_connection,
        parse_authority=_parse_authority,
        parse_http_target=_parse_http_target,
        origin_request_header=_origin_request_header,
        relay_both_directions=_relay_both_directions,
        rejected_error=DestinationRejected,
        header_limit=MAX_REQUEST_HEADER_BYTES,
        timeout_seconds=CONNECT_TIMEOUT_SECONDS,
    )


async def start_proxy(host: str = "127.0.0.1", port: int = 0) -> asyncio.AbstractServer:
    """Start the secure proxy on an explicitly loopback-only listener."""

    if host not in {"127.0.0.1", "::1"}:
        raise ValueError("Secure egress proxy may bind only to loopback")
    return await asyncio.start_server(handle_proxy_client, host=host, port=port, limit=MAX_REQUEST_HEADER_BYTES)


async def serve_forever(state_file: Path, host: str = "127.0.0.1", port: int = 0) -> None:
    """Publish private state then run the proxy until its process is stopped."""

    await _server.serve_forever(state_file, start_proxy, host, port)


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
