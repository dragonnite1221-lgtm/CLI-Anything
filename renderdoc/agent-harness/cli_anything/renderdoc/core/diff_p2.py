# ruff: noqa: F403, F405, E501
from .diff_base import *  # noqa: F403

# fmt: off
from .diff_p1 import _diff_dicts, _diff_lists, _values_equal  # noqa: E402,E501
# fmt: on


def _diff_cbuffer_vars(
    vars_a: List[Dict],
    vars_b: List[Dict],
) -> Optional[List[Dict]]:
    """Compare two lists of cbuffer variables; return only diffs."""
    a_map = {v["name"]: v for v in vars_a}
    b_map = {v["name"]: v for v in vars_b}
    all_names = sorted(set(list(a_map.keys()) + list(b_map.keys())))

    diffs = []
    for name in all_names:
        va = a_map.get(name)
        vb = b_map.get(name)
        if va is None:
            diffs.append({"name": name, "status": "only_in_B", "B": vb})
        elif vb is None:
            diffs.append({"name": name, "status": "only_in_A", "A": va})
        else:
            if "members" in va or "members" in vb:
                sub = _diff_cbuffer_vars(
                    va.get("members", []),
                    vb.get("members", []),
                )
                if sub:
                    diffs.append({"name": name, "status": "changed", "members": sub})
            else:
                vals_a = va.get("values", [])
                vals_b = vb.get("values", [])
                if not _values_equal(vals_a, vals_b):
                    diffs.append(
                        {
                            "name": name,
                            "status": "changed",
                            "A": vals_a,
                            "B": vals_b,
                        }
                    )

    return diffs if diffs else None


def _diff_bindings(bindings_a: Dict, bindings_b: Dict) -> Optional[Dict[str, Any]]:
    """Diff the bindings sub-dict of a stage.

    Handles: constantBlocks (with nested variable values),
    readOnlyResources, readWriteResources, samplers.
    """
    result: Dict[str, Any] = {}
    has_diff = False

    # --- constantBlocks ---
    cbs_a = bindings_a.get("constantBlocks", [])
    cbs_b = bindings_b.get("constantBlocks", [])

    # Build maps keyed by index
    a_map = {cb.get("index", i): cb for i, cb in enumerate(cbs_a)}
    b_map = {cb.get("index", i): cb for i, cb in enumerate(cbs_b)}
    all_indices = sorted(set(list(a_map.keys()) + list(b_map.keys())))

    cb_diffs = []
    var_diffs_all = []
    for idx in all_indices:
        ca = a_map.get(idx)
        cb_ = b_map.get(idx)
        if ca is None:
            cb_diffs.append({"index": idx, "status": "only_in_B", "B": cb_})
        elif cb_ is None:
            cb_diffs.append({"index": idx, "status": "only_in_A", "A": ca})
        else:
            # Compare binding metadata (resource, byteOffset, byteSize)
            ca_meta = {k: v for k, v in ca.items() if k not in ("variables",)}
            cb_meta = {k: v for k, v in cb_.items() if k not in ("variables",)}
            meta_diff = _diff_dicts(ca_meta, cb_meta)
            if meta_diff:
                cb_diffs.append(
                    {"index": idx, "status": "changed", "fields": meta_diff}
                )

            # Compare runtime variable values
            va_vars = ca.get("variables", [])
            vb_vars = cb_.get("variables", [])
            vdiff = _diff_cbuffer_vars(va_vars, vb_vars)
            if vdiff:
                var_diffs_all.append({"index": idx, "variables": vdiff})

    cb_result: Dict[str, Any] = {}
    if cb_diffs:
        cb_result["metadata"] = cb_diffs
    if var_diffs_all:
        cb_result["variables"] = var_diffs_all

    if cb_result:
        result["constantBlocks"] = cb_result
        has_diff = True
    else:
        result["constantBlocks"] = "SAME"

    # --- readOnlyResources, readWriteResources, samplers ---
    for section in ("readOnlyResources", "readWriteResources", "samplers"):
        d = _diff_lists(
            bindings_a.get(section, []),
            bindings_b.get(section, []),
            key_field="index",
        )
        if d:
            result[section] = d
            has_diff = True
        else:
            result[section] = "SAME"

    return result if has_diff else None
