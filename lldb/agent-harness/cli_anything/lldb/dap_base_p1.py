# ruff: noqa: F403, F405, E501
from .dap_base_base import *  # noqa: F403


class DAPProtocolError(RuntimeError):
    """Raised when a DAP frame cannot be parsed."""


def encode_message(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    return header + body


def _raise_protocol_error(message: str):
    raise DAPProtocolError(message)


def read_message(stream: BinaryIO) -> dict[str, Any] | None:
    content_length: int | None = None
    saw_header = False

    while True:
        line = stream.readline()
        if line == b"":
            return (
                None
                if not saw_header
                else _raise_protocol_error("Unexpected EOF in DAP header")
            )
        saw_header = True
        stripped = line.strip()
        if not stripped:
            break
        name, sep, value = stripped.partition(b":")
        if not sep:
            raise DAPProtocolError(f"Malformed DAP header: {stripped!r}")
        if name.lower() == b"content-length":
            try:
                content_length = int(value.strip())
            except ValueError as exc:
                raise DAPProtocolError(f"Invalid Content-Length: {value!r}") from exc

    if content_length is None:
        raise DAPProtocolError("Missing Content-Length header")

    body = stream.read(content_length)
    if len(body) != content_length:
        raise DAPProtocolError("Unexpected EOF in DAP body")
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise DAPProtocolError(f"Invalid DAP JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise DAPProtocolError("DAP payload must be a JSON object")
    return payload


def _first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value is not None and not (isinstance(value, str) and value == ""):
            return value
    return None


def _stop_field_matches(
    expected: str,
    values: list[Any],
    *,
    allow_basename: bool = False,
    allow_symbol_suffix: bool = False,
) -> bool:
    expected_norm = expected.casefold()
    for value in values:
        if value is None:
            continue
        text = str(value)
        candidates = [text.casefold()]
        if allow_basename:
            candidates.append(Path(text).name.casefold())
        for candidate in candidates:
            if candidate == expected_norm:
                return True
            if allow_symbol_suffix and (
                candidate.endswith(f"::{expected_norm}")
                or candidate.endswith(f"`{expected_norm}")
            ):
                return True
    return False


def _stop_context_text(stop_context: dict[str, Any]) -> str:
    fields = [
        stop_context.get("reason"),
        stop_context.get("lldbReason"),
        stop_context.get("description"),
        stop_context.get("module"),
        stop_context.get("modulePath"),
        stop_context.get("function"),
    ]
    frame = stop_context.get("frame")
    if isinstance(frame, dict):
        fields.extend(
            frame.get(key)
            for key in ("module", "module_path", "function", "file", "address")
        )
    return "\n".join(str(field) for field in fields if field)
