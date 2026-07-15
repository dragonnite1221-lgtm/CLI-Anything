"""Private-network / SSRF host detection for the browser harness.

Regex host matching (the previous approach) misses decimal (``2130706433``),
hex (``0x7f000001``), octal, and IPv4-mapped-IPv6 encodings of private
addresses, and cannot see DNS-rebinding targets. This module resolves the
host to concrete IPs (literal parse + ``getaddrinfo``) and classifies each with
the stdlib ``ipaddress`` module, so every encoding of a private/loopback/
link-local/reserved address is caught.
"""

from __future__ import annotations

import ipaddress
import socket


def _classify(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    # Unwrap ::ffff:127.0.0.1 style IPv4-mapped IPv6 to judge the inner v4.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_unspecified
        or ip.is_multicast
    )


def _literal_ips(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    candidate = host.strip().strip("[]")
    parsers = (
        lambda h: ipaddress.ip_address(h),          # dotted v4 / v6
        lambda h: ipaddress.ip_address(int(h)),     # decimal, e.g. 2130706433
        lambda h: ipaddress.ip_address(int(h, 16)), # hex, e.g. 0x7f000001
        lambda h: ipaddress.ip_address(int(h, 8)),  # octal
    )
    for parse in parsers:
        try:
            return [parse(candidate)]
        except (ValueError, TypeError):
            continue
    return []


def host_is_private(host: str) -> bool:
    """True if ``host`` resolves to any private/loopback/reserved address.

    Checks literal IP encodings first, then falls back to ``getaddrinfo`` so
    hostnames that resolve to private space (DNS rebinding) are also blocked.
    A resolution failure (offline / unknown host) is not treated as private —
    only addresses we can actually classify are blocked.
    """
    candidates = _literal_ips(host)
    try:
        for info in socket.getaddrinfo(host, None):
            candidates.append(ipaddress.ip_address(info[4][0]))
    except (socket.gaierror, OSError, ValueError, UnicodeError):
        pass
    return any(_classify(ip) for ip in candidates)
