# ruff: noqa: F403, F405, E501
from .extract_tools_base import *  # noqa: F403


def _decode_js_string(inner: str) -> str:
    """Decode a JS string literal's escape sequences safely.

    We cannot use ``bytes.decode('unicode_escape')`` because it assumes
    latin-1 input, which corrupts multi-byte UTF-8 characters. Instead we
    handle the JS escapes we actually care about and leave the rest alone.
    """

    def _replace(m: re.Match) -> str:
        esc = m.group(0)
        if esc == '\\"':
            return '"'
        if esc == "\\'":
            return "'"
        if esc == "\\\\":
            return "\\"
        if esc == "\\n":
            return "\n"
        if esc == "\\r":
            return "\r"
        if esc == "\\t":
            return "\t"
        if esc == "\\b":
            return "\b"
        if esc == "\\f":
            return "\f"
        if esc == "\\/":
            return "/"
        if esc.startswith("\\u"):
            try:
                return chr(int(esc[2:], 16))
            except ValueError:
                return esc
        if esc.startswith("\\x"):
            try:
                return chr(int(esc[2:], 16))
            except ValueError:
                return esc
        return esc

    return re.sub(
        r'\\(?:["\'\\/bfnrt]|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2})',
        _replace,
        inner,
    )


def _skip_ws(src: str, pos: int) -> int:
    while pos < len(src) and src[pos] in " \t\r\n":
        pos += 1
    return pos


def _skip_ws_comma(src: str, pos: int) -> int:
    pos = _skip_ws(src, pos)
    if pos < len(src) and src[pos] == ",":
        pos += 1
    return _skip_ws(src, pos)


def _find_string_end(src: str, start: int) -> int:
    """Return index of the closing quote for a double-quoted string."""
    if src[start] != '"':
        return -1
    i = start + 1
    while i < len(src):
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == '"':
            return i
        i += 1
    return -1


def _find_brace_end(src: str, start: int) -> int:
    """Find the matching closing brace, respecting strings and nesting."""
    if src[start] != "{":
        return -1
    depth = 1
    i = start + 1
    while i < len(src):
        c = src[i]
        if c == '"':
            end = _find_string_end(src, i)
            if end == -1:
                return -1
            i = end + 1
            continue
        if c == "'":
            i += 1
            while i < len(src) and src[i] != "'":
                i += 2 if src[i] == "\\" else 1
            i += 1
            continue
        if c == "/" and i + 1 < len(src) and src[i + 1] == "/":
            while i < len(src) and src[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < len(src) and src[i + 1] == "*":
            i += 2
            while i + 1 < len(src) and not (src[i] == "*" and src[i + 1] == "/"):
                i += 1
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1
