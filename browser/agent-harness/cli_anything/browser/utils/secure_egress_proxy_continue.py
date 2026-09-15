"""Expect: 100-continue relaying for the one-request HTTP forwarder.

Split out of secure_egress_proxy_http.py to keep both files under the
200-line file-size gate (.github/scripts/check_file_size.py).
"""

from __future__ import annotations

import asyncio

# RFC 9110 10.1.1 permits a destination to omit the 100-Continue response
# entirely and just read the request body directly -- there is no way to
# tell "not sending one" apart from "about to send one" except by waiting.
# The same section tells *clients* not to wait indefinitely for exactly
# this reason. Mirror that with a short, bounded grace period instead of
# the full per-operation timeout, so a destination that silently proceeds
# doesn't deadlock this relay for the whole connection timeout.
CONTINUE_GRACE_SECONDS = 1


class NoInterimResponse(Exception):
    """No response has started arriving within the grace period.

    Distinct from a plain asyncio.TimeoutError so relay_http_request can
    tell "the destination may just be skipping the interim response
    entirely" (safe to give up on and proceed) apart from "a response
    already started but stalled partway through" (a genuine failure that
    must not be papered over -- the client has already received a partial
    status line/headers by that point, and silently forwarding the body
    afterward would corrupt the response framing).
    """


def expects_continue(headers: list[str]) -> bool:
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


async def _read_status_line(
    reader: asyncio.StreamReader, initial_timeout_seconds: int, continuation_timeout_seconds: int
) -> bytes:
    """Read one CRLF-terminated status line, applying the short grace
    period only to whether *any* byte of it arrives at all.

    ``readuntil(...)`` is a single atomic wait for the full delimiter, so
    timing the whole call with the short grace period would also abandon a
    response that has already started arriving (e.g. "HTTP/1.1 100 " sent,
    then a pause before the rest) -- indistinguishable, from the outside,
    from one that never started. Reading the first byte on its own settles
    that distinction: nothing within the grace period really means no
    response is coming; anything at all means the destination has already
    committed to one, and finishing that line is then governed by the
    normal continuation timeout like every other read in this function.
    """
    try:
        first_byte = await asyncio.wait_for(reader.read(1), timeout=initial_timeout_seconds)
    except asyncio.TimeoutError:
        raise NoInterimResponse from None
    if not first_byte:
        raise NoInterimResponse  # destination closed before sending anything
    rest = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=continuation_timeout_seconds)
    return first_byte + rest


async def relay_interim_response(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    initial_timeout_seconds: int,
    continuation_timeout_seconds: int,
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

    `initial_timeout_seconds` (short) bounds only the wait for whether a
    *new* response starts at all -- a destination is allowed to never send
    one and just read the body directly, so the caller needs to give up
    quickly on that possibility rather than block for the full per-request
    timeout. Once a status line has actually started arriving,
    `continuation_timeout_seconds` (the normal per-request timeout) governs
    finishing that same response's headers -- a destination that answered
    within the grace period but is merely slow to finish writing its
    headers has already committed to a response, and must not be treated
    as if it had gone silent.
    """

    while True:
        status_line = await _read_status_line(reader, initial_timeout_seconds, continuation_timeout_seconds)
        writer.write(status_line)
        await writer.drain()
        while True:
            line = await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=continuation_timeout_seconds)
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
