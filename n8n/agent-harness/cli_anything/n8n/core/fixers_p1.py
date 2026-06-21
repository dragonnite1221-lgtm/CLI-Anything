# ruff: noqa: F403, F405, E501
from .fixers_base import *  # noqa: F403


@dataclass
class Fix:
    """A single fix that can be applied to a workflow."""

    fix_type: str
    description: str
    confidence: str  # HIGH, MEDIUM, LOW
    node_name: str | None = None


def _iter_params(params: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
    """Recursively iterate parameter key-value pairs.

    Returns (dotted_key, string_value) tuples. Keys with list indices use
    bracket notation: 'assignments[0].value'.
    Note: _set_nested handles these bracket keys correctly.
    """
    result = []
    for k, v in params.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.extend(_iter_params(v, full_key))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    result.extend(_iter_params(item, f"{full_key}[{i}]"))
                elif isinstance(item, str):
                    result.append((f"{full_key}[{i}]", item))
        elif isinstance(v, str):
            result.append((full_key, v))
    return result


_KEY_PART_RE = re.compile(r"([^\[.\]]+)|\[(\d+)\]")


def _set_nested(d: dict[str, Any], key: str, value: Any) -> bool:
    """Set a nested value using dot/bracket notation.

    Handles keys like 'a.b', 'a[0].b', 'a.b[1].c' correctly,
    navigating into both dicts and lists. Returns True if value was set.
    """
    parts: list[str | int] = []
    for match in _KEY_PART_RE.finditer(key):
        if match.group(1) is not None:
            parts.append(match.group(1))
        elif match.group(2) is not None:
            parts.append(int(match.group(2)))

    if not parts:
        return False

    current: Any = d
    for part in parts[:-1]:
        if isinstance(part, int):
            if isinstance(current, list) and 0 <= part < len(current):
                current = current[part]
            else:
                return False
        else:
            if isinstance(current, dict):
                current = current.setdefault(part, {})
            else:
                return False

    last = parts[-1]
    if isinstance(last, int):
        if isinstance(current, list) and 0 <= last < len(current):
            current[last] = value
            return True
        return False
    elif isinstance(current, dict):
        current[last] = value
        return True
    return False
