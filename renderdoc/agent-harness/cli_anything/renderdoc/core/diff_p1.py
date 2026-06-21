# ruff: noqa: F403, F405, E501
from .diff_base import *  # noqa: F403


def _floats_equal(a, b) -> bool:
    """Compare two floats with tolerance; handle NaN/Inf."""
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        if math.isinf(a) and math.isinf(b):
            return a == b
        return abs(a - b) <= _FLOAT_TOL
    return a == b


def _values_equal(a, b) -> bool:
    """Deep equality check for plain JSON-like values."""
    if type(a) != type(b):
        return False
    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(_values_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(_values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, float):
        return _floats_equal(a, b)
    return a == b


def _diff_dicts(
    a: Optional[Dict],
    b: Optional[Dict],
    label: str = "",
) -> Optional[Dict[str, Any]]:
    """Compare two flat/nested dicts, return only differing keys.

    Returns None if both are equal (or both None).
    """
    if a is None and b is None:
        return None
    if a is None or b is None:
        return {"A": a, "B": b}

    diffs: Dict[str, Any] = {}
    all_keys = sorted(set(list(a.keys()) + list(b.keys())))
    for k in all_keys:
        va = a.get(k)
        vb = b.get(k)
        if not _values_equal(va, vb):
            diffs[k] = {"A": va, "B": vb}

    return diffs if diffs else None


def _diff_lists(
    a: Optional[List],
    b: Optional[List],
    key_field: str = "name",
) -> Optional[List[Dict[str, Any]]]:
    """Compare two lists of dicts by a key field, return only diffs.

    Items present in A but not B get status "only_in_A", vice versa.
    Items present in both get per-field diff.
    Returns None if identical.
    """
    if a is None and b is None:
        return None
    a = a or []
    b = b or []

    a_map = {str(item.get(key_field, i)): item for i, item in enumerate(a)}
    b_map = {str(item.get(key_field, i)): item for i, item in enumerate(b)}
    all_keys = sorted(set(list(a_map.keys()) + list(b_map.keys())))

    diffs = []
    for k in all_keys:
        va = a_map.get(k)
        vb = b_map.get(k)
        if va is None:
            diffs.append({"key": k, "status": "only_in_B", "B": vb})
        elif vb is None:
            diffs.append({"key": k, "status": "only_in_A", "A": va})
        else:
            d = _diff_dicts(va, vb)
            if d:
                diffs.append({"key": k, "status": "changed", "fields": d})

    return diffs if diffs else None
