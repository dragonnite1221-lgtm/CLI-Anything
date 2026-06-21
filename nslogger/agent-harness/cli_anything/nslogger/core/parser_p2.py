# ruff: noqa: F403, F405, E501
from .parser_base import *  # noqa: F403

# fmt: off
from .parser_p1 import ParseError, _parse_message_payload  # noqa: E402,E501
# fmt: on


def _parse_message(raw: bytes) -> LogMessage:
    """Parse a single wire-protocol message from raw bytes.

    NSLogger's native wire format is:
    [partCount][parts...]

    Older local test fixtures in this repo used:
    [sequence][partCount][parts...]
    We keep a best-effort fallback for those fixtures.
    """
    if len(raw) < 2:
        raise ParseError("Message too short")

    # Native NSLogger format: payload begins with partCount.
    try:
        msg = _parse_message_payload(raw, 0, implicit_int_sizes=True)
        if (
            msg.message_type != MSG_TYPE_LOG
            or msg.text
            or msg.client_name
            or msg.image_data
            or msg.binary_data
        ):
            return msg
    except ParseError:
        pass

    # Older generated fixtures used official part keys but still wrote a
    # redundant 4-byte size before integer values.
    try:
        msg = _parse_message_payload(raw, 0, implicit_int_sizes=False)
        if (
            msg.message_type != MSG_TYPE_LOG
            or msg.text
            or msg.client_name
            or msg.image_data
            or msg.binary_data
        ):
            return msg
    except ParseError:
        pass

    # Backward-compatible fallback for historical local fixtures.
    if len(raw) < 6:
        raise ParseError("Message too short")
    seq = struct.unpack(">I", raw[0:4])[0]
    try:
        return _parse_message_payload(
            raw, 4, initial_sequence=seq, implicit_int_sizes=False
        )
    except ParseError:
        return _parse_message_payload(
            raw, 4, initial_sequence=seq, implicit_int_sizes=True
        )


def parse_raw_file(path: str) -> Iterator[LogMessage]:
    """Yield LogMessage objects from a .rawnsloggerdata file."""
    with open(path, "rb") as f:
        while True:
            header = f.read(4)
            if not header:
                break
            if len(header) < 4:
                raise ParseError(
                    f"Truncated file: got {len(header)} bytes in length header"
                )
            msg_len = struct.unpack(">I", header)[0]
            if msg_len == 0:
                continue
            raw = f.read(msg_len)
            if len(raw) < msg_len:
                break
            try:
                yield _parse_message(raw)
            except ParseError:
                continue


def _parse_nsloggerdata(path: str) -> Iterator[LogMessage]:
    """Parse .nsloggerdata binary plist files via Python plistlib."""
    import plistlib

    try:
        with open(path, "rb") as f:
            data = plistlib.load(f)
        # NSLogger saves as a plist dict with 'messages' array
        messages = data if isinstance(data, list) else data.get("messages", [])
        for i, m in enumerate(messages):
            if not isinstance(m, dict):
                continue
            msg = LogMessage(sequence=i)
            ts = m.get("timestamp")
            if ts is not None:
                try:
                    msg.timestamp = datetime.fromtimestamp(float(ts), tz=timezone.utc)
                    frac = float(ts) - int(float(ts))
                    msg.timestamp_ms = int(frac * 1000)
                except (TypeError, ValueError):
                    pass
            msg.tag = str(m.get("tag", ""))
            msg.level = int(m.get("level", 2))
            msg.thread_id = str(m.get("threadID", ""))
            msg.text = str(m.get("message", m.get("messageText", "")))
            yield msg
    except Exception:
        # Try raw protocol as fallback
        yield from parse_raw_file(path)


def parse_file(path: str) -> Iterator[LogMessage]:
    """Auto-detect format and parse .rawnsloggerdata or .nsloggerdata files."""
    if path.endswith(".rawnsloggerdata"):
        yield from parse_raw_file(path)
    else:
        # .nsloggerdata is a binary plist wrapping archived messages
        # Fall back to raw parser which handles both (raw starts with length)
        yield from _parse_nsloggerdata(path)
