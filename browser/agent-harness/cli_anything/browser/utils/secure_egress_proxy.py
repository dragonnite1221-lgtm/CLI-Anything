"""Loopback-only proxy admission checks with DNS-pinned destination selection."""

from __future__ import annotations

import argparse
import asyncio
import ipaddress
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from cli_anything.browser.utils import secure_egress_proxy_server as _server
from cli_anything.browser.utils import secure_egress_proxy_parsing as _parsing


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


def _validated_addresses(infos) -> tuple[str, ...]:
    """Reject a resolver response containing an invalid or non-public address."""

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


def _global_addresses(host: str, port: int) -> tuple[str, ...]:
    """Resolve once and reject a response containing any non-global address."""

    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, OSError, UnicodeError) as error:
        raise DestinationRejected("Destination hostname could not be resolved") from error
    return _validated_addresses(infos)


def _validate_destination(host: str, port: int) -> None:
    if not isinstance(host, str) or not host or any(char.isspace() for char in host):
        raise DestinationRejected("Destination hostname is invalid")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise DestinationRejected("Destination port is invalid")


def resolve_pinned_destination(host: str, port: int) -> PinnedDestination:
    """Validate a destination and retain every resolved numeric address."""

    _validate_destination(host, port)
    return PinnedDestination(host=host, port=port, addresses=_global_addresses(host, port))


async def _resolve_pinned_destination(host: str, port: int) -> PinnedDestination:
    """Resolve through asyncio's worker pool so a slow resolver cannot stall active tunnels."""

    _validate_destination(host, port)
    try:
        infos = await asyncio.wait_for(
            asyncio.get_running_loop().getaddrinfo(host, port, type=socket.SOCK_STREAM),
            timeout=CONNECT_TIMEOUT_SECONDS,
        )
    except (socket.gaierror, OSError, UnicodeError, asyncio.TimeoutError) as error:
        raise DestinationRejected("Destination hostname could not be resolved") from error
    return PinnedDestination(host=host, port=port, addresses=_validated_addresses(infos))


async def open_pinned_connection(host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    """Connect to the validated numeric address, never a caller-controlled hostname."""

    destination = await _resolve_pinned_destination(host, port)
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

    return _parsing.parse_authority(value, DestinationRejected)


def _parse_http_target(target: str) -> tuple[str, int, str]:
    """Return host, port, and origin-form target for an HTTP proxy request."""

    return _parsing.parse_http_target(target, DestinationRejected)


def _origin_request_header(method: str, path: str, version: str, headers: Iterable[str]) -> bytes:
    """Convert an absolute-form proxy request to an origin-form request."""

    return _parsing.origin_request_header(method, path, version, headers, DestinationRejected)


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
