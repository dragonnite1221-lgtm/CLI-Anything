# ruff: noqa: F403, F405, E501
from .extract_tools_base import *  # noqa: F403

# fmt: off
from .extract_tools_p1 import _find_string_end  # noqa: E402,E501
# fmt: on


def _split_top_level(src: str, sep: str) -> list[str]:
    """Split on `sep` at depth 0 (outside brackets/parens/strings)."""
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    i = 0
    while i < len(src):
        c = src[i]
        if c == '"':
            end = _find_string_end(src, i)
            if end == -1:
                buf.append(src[i:])
                break
            buf.append(src[i : end + 1])
            i = end + 1
            continue
        if c == "'":
            start = i
            i += 1
            while i < len(src) and src[i] != "'":
                i += 2 if src[i] == "\\" else 1
            if i >= len(src):
                # Unterminated single-quoted string; bail
                buf.append(src[start:])
                break
            buf.append(src[start : i + 1])
            i += 1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if c == sep and depth == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    if buf:
        parts.append("".join(buf))
    return parts


_TYPE_MAP = {
    "string": "string",
    "number": "number",
    "boolean": "boolean",
    "array": "array",
    "object": "object",
    "enum": "string",  # enums become strings with choices
    "literal": "string",  # literals become strings with one choice
    "any": "string",
    "unknown": "string",
    "null": "null",
    "nullable": "string",
    "record": "object",
}


def _find_matching_paren(src: str, open_pos: int) -> int:
    """Find the index of the ')' matching the '(' at open_pos."""
    if open_pos >= len(src) or src[open_pos] != "(":
        return -1
    depth = 1
    i = open_pos + 1
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
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1
