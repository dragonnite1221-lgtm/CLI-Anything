"""HTTP proxy request parsers kept separate from DNS-pinning transport policy."""

from __future__ import annotations

from typing import Iterable
from urllib.parse import urlsplit


def parse_authority(value: str, rejected_error) -> tuple[str, int]:
    """Parse a CONNECT authority without accepting user-info."""

    if value.startswith("["):
        closing = value.find("]")
        if closing < 0 or not value[closing + 1 :].startswith(":"):
            raise rejected_error("CONNECT authority must include a port")
        host, port_text = value[1:closing], value[closing + 2 :]
    else:
        host, separator, port_text = value.rpartition(":")
        if not separator:
            raise rejected_error("CONNECT authority must include a port")
    if "@" in host:
        raise rejected_error("CONNECT authority must not include credentials")
    try:
        port = int(port_text, 10)
    except ValueError as error:
        raise rejected_error("CONNECT port is invalid") from error
    if not host or not 1 <= port <= 65535:
        raise rejected_error("CONNECT authority is invalid")
    return host, port


def parse_http_target(target: str, rejected_error) -> tuple[str, int, str]:
    """Return host, port, and origin-form target for an HTTP proxy request."""

    parsed = urlsplit(target)
    if parsed.scheme.lower() != "http" or not parsed.hostname:
        raise rejected_error("Proxy request must use an absolute http URL")
    if parsed.username is not None or parsed.password is not None:
        raise rejected_error("Proxy request must not include credentials")
    try:
        port = parsed.port or 80
    except ValueError as error:
        raise rejected_error("Proxy request port is invalid") from error
    path = parsed.path or "/"
    return parsed.hostname, port, f"{path}?{parsed.query}" if parsed.query else path


def origin_request_header(method: str, path: str, version: str, headers: Iterable[str], rejected_error) -> bytes:
    """Convert an absolute-form proxy request to a close-delimited origin request."""

    forwarded = [f"{method} {path} {version}"]
    for header in headers:
        name, separator, _value = header.partition(":")
        if not separator:
            raise rejected_error("Proxy request header is malformed")
        if name.lower() not in {"connection", "proxy-connection", "proxy-authorization"}:
            forwarded.append(header)
    forwarded.append("Connection: close")
    return ("\r\n".join(forwarded) + "\r\n\r\n").encode("iso-8859-1")
