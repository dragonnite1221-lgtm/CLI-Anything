# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project  # noqa: E402,E501
# fmt: on


def datum_point(
    project: Dict[str, Any],
    body_index: int,
    position: Optional[List[float]] = None,
    attachment_mode: Optional[str] = None,
    attachment_refs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a datum point to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    position:
        Point position ``[x, y, z]``.  Defaults to ``[0, 0, 0]``.

    Returns
    -------
    Dict[str, Any]
        The newly created datum point feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    if position is None:
        position = [0, 0, 0]
    if not isinstance(position, (list, tuple)) or len(position) != 3:
        raise ValueError("Position must be a list of 3 numbers")
    position = [float(v) for v in position]

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "datum_point",
        "position": position,
    }

    if attachment_mode is not None:
        if attachment_mode not in VALID_ATTACHMENT_MODES:
            raise ValueError(
                f"Invalid attachment_mode '{attachment_mode}'. Valid: {sorted(VALID_ATTACHMENT_MODES)}"
            )
        feature["attachment_mode"] = attachment_mode
    if attachment_refs is not None:
        feature["attachment_refs"] = attachment_refs

    body["features"].append(feature)
    return feature


def local_coordinate_system(
    project: Dict[str, Any],
    body_index: int,
    position: Optional[List[float]] = None,
    x_axis: Optional[List[float]] = None,
    y_axis: Optional[List[float]] = None,
    z_axis: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Add a local coordinate system to a body (FreeCAD 1.1).

    Replaces the legacy Origin object with a fully configurable
    coordinate system that supports cross-workbench attachment.
    """
    bodies = project.get("bodies", [])
    if body_index < 0 or body_index >= len(bodies):
        raise IndexError(
            f"Body index {body_index} out of range (0..{len(bodies) - 1})."
        )
    body = bodies[body_index]
    feature: Dict[str, Any] = {
        "type": "local_coordinate_system",
        "position": position or [0.0, 0.0, 0.0],
        "x_axis": x_axis or [1.0, 0.0, 0.0],
        "y_axis": y_axis or [0.0, 1.0, 0.0],
        "z_axis": z_axis or [0.0, 0.0, 1.0],
    }
    body.setdefault("features", []).append(feature)
    return feature


def shape_binder(
    project: Dict[str, Any],
    body_index: int,
    source_body_index: int,
    feature_ref: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a shape binder referencing geometry from another body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    source_body_index:
        Index of the source body containing the geometry to bind.
    feature_ref:
        Optional feature reference identifier in the source body
        (e.g. ``"Pad"``).  If ``None``, binds the entire shape.

    Returns
    -------
    Dict[str, Any]
        The newly created shape binder feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)
    _get_body(project, source_body_index)  # validate source exists

    if body_index == source_body_index:
        raise ValueError("Shape binder source and target bodies must be different")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "shape_binder",
        "source_body_index": source_body_index,
        "feature_ref": feature_ref,
    }

    body["features"].append(feature)
    return feature
