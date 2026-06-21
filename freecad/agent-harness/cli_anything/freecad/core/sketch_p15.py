# ruff: noqa: F403, F405, E501
from .sketch_base import *  # noqa: F403

# fmt: off
from .sketch_p1 import _get_sketch, _validate_project  # noqa: E402,E501
# fmt: on


def validate_sketch(
    project: Dict[str, Any],
    sketch_index: int,
) -> Dict[str, Any]:
    """Check sketch validity.

    Performs basic validation: ensures the sketch has elements and that
    all constraint element references are valid.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.

    Returns
    -------
    Dict[str, Any]
        Validation result with ``valid`` flag and list of ``issues``.
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    issues: List[str] = []
    elements = sketch.get("elements", [])
    constraints = sketch.get("constraints", [])

    if not elements:
        issues.append("Sketch has no elements")

    existing_ids = {el["id"] for el in elements}
    for c in constraints:
        for eid in c.get("elements", []):
            if eid not in existing_ids:
                issues.append(
                    f"Constraint {c['id']} references non-existent element {eid}"
                )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "element_count": len(elements),
        "constraint_count": len(constraints),
    }


def solve_status(
    project: Dict[str, Any],
    sketch_index: int,
) -> Dict[str, Any]:
    """Return the constraint solving status of a sketch.

    Provides an estimate of the degrees of freedom (DOF) and whether the
    sketch is fully, under, or over constrained.

    Parameters
    ----------
    project:
        The project dictionary.
    sketch_index:
        Index of the target sketch.

    Returns
    -------
    Dict[str, Any]
        Status containing ``status``, ``element_count``,
        ``constraint_count``, and ``dof`` (estimated degrees of freedom).
    """
    _validate_project(project)
    sketch = _get_sketch(project, sketch_index)

    elements = sketch.get("elements", [])
    constraints = sketch.get("constraints", [])

    # Rough DOF estimation: each element contributes DOF based on type,
    # each constraint removes 1 DOF.
    dof_per_type = {
        "point": 2,
        "line": 4,
        "circle": 3,
        "arc": 5,
        "ellipse": 5,
        "bspline": 2,  # per pole, but simplified
    }

    total_dof = 0
    for el in elements:
        etype = el.get("type", "line")
        if etype == "bspline":
            total_dof += len(el.get("poles", [])) * 2
        else:
            total_dof += dof_per_type.get(etype, 4)

    total_dof -= len(constraints)

    if total_dof == 0:
        status = "fully_constrained"
    elif total_dof > 0:
        status = "under_constrained"
    else:
        status = "over_constrained"

    return {
        "status": status,
        "element_count": len(elements),
        "constraint_count": len(constraints),
        "dof": total_dof,
    }
