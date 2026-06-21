# ruff: noqa: F403, F405, E501
from .measure_base import *  # noqa: F403

# fmt: off
from .measure_p1 import _store_measurement  # noqa: E402,E501
from .measure_p2 import _compute_inertia  # noqa: E402,E501
# fmt: on


def measure_inertia(
    project: Dict[str, Any], index: int, additive: bool = False
) -> Dict[str, Any]:
    """Estimate the principal moments of inertia (unit density).

    Returns
    -------
    dict
        Measurement record with ``Ixx``, ``Iyy``, ``Izz`` values.
    """
    part = get_part(project, index)
    inertia = _compute_inertia(part)

    if inertia is not None:
        inertia = {k: round(v, 6) for k, v in inertia.items()}

    result_inertia: Dict[str, Any] = {
        "part_index": index,
        "inertia": inertia,
        "deferred": inertia is None,
    }
    if additive:
        result_inertia["additive"] = True
    return _store_measurement(project, "inertia", result_inertia)


def check_geometry(
    project: Dict[str, Any],
    index: int,
    include_valid: bool = False,
    skip_objects: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Perform basic geometry validation on a part.

    Checks that all numeric parameters are positive and that the part
    type is a known primitive.

    Parameters
    ----------
    project : dict
        The mutable project state dictionary.
    index : int
        Index of the part in ``project["parts"]``.
    include_valid : bool
        When ``True``, also reports valid shape entries in ``valid_entries``
        (default ``False``).
    skip_objects : list[int] or None
        When provided, excludes these part indices from the check.  If the
        requested *index* is in the skip list the result is returned
        immediately with ``"skipped": True``.

    Returns
    -------
    dict
        Record with ``valid`` boolean and list of ``issues``.
    """
    if skip_objects is not None and index in skip_objects:
        return _store_measurement(
            project,
            "geometry_check",
            {
                "part_index": index,
                "valid": True,
                "issues": [],
                "skipped": True,
            },
        )

    part = get_part(project, index)
    issues: List[str] = []
    valid_entries: List[str] = []

    t = part["type"]
    if t not in PRIMITIVES:
        issues.append(f"Unknown primitive type '{t}'")
    else:
        p = part["params"]
        defaults = PRIMITIVES[t]
        for key in defaults:
            if key in p:
                val = p[key]
                # Angle parameters may be negative (e.g. angle1 on sphere/torus)
                if "angle" not in key and val <= 0:
                    issues.append(f"Parameter '{key}' must be positive, got {val}")
                elif include_valid:
                    valid_entries.append(f"Parameter '{key}' = {val}")
            else:
                issues.append(f"Missing expected parameter '{key}'")

    # Validate placement exists
    placement = part.get("placement")
    if placement is None:
        issues.append("Missing 'placement' on part")
    else:
        if "position" not in placement:
            issues.append("Missing 'position' in placement")
        elif include_valid:
            valid_entries.append("Placement 'position' present")
        if "rotation" not in placement:
            issues.append("Missing 'rotation' in placement")
        elif include_valid:
            valid_entries.append("Placement 'rotation' present")

    result: Dict[str, Any] = {
        "part_index": index,
        "valid": len(issues) == 0,
        "issues": issues,
    }
    if include_valid:
        result["valid_entries"] = valid_entries
    if skip_objects is not None:
        result["skipped"] = False

    return _store_measurement(project, "geometry_check", result)
