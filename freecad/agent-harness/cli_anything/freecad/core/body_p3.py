# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403

# fmt: off
from .body_p1 import _get_body, _next_feature_id, _validate_project  # noqa: E402,E501
# fmt: on


def fillet(
    project: Dict[str, Any],
    body_index: int,
    radius: float = 1.0,
    edges: Union[str, List[int]] = "all",
) -> Dict[str, Any]:
    """Add a fillet (rounded edge) feature to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    radius:
        Fillet radius.  Must be positive.
    edges:
        ``"all"`` to fillet every edge, or a list of edge indices.

    Returns
    -------
    Dict[str, Any]
        The newly created fillet feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    radius = float(radius)
    if radius <= 0:
        raise ValueError(f"Fillet radius must be positive, got {radius}")

    if edges != "all":
        if not isinstance(edges, (list, tuple)):
            raise ValueError("Edges must be 'all' or a list of edge indices")
        for idx in edges:
            if not isinstance(idx, int) or idx < 0:
                raise ValueError(
                    f"Edge index must be a non-negative integer, got {idx!r}"
                )
        edges = list(edges)

    if not body["features"]:
        raise ValueError("Cannot add fillet to a body with no existing features")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "fillet",
        "radius": radius,
        "edges": edges,
    }

    body["features"].append(feature)
    return feature


def chamfer(
    project: Dict[str, Any],
    body_index: int,
    size: float = 1.0,
    edges: Union[str, List[int]] = "all",
) -> Dict[str, Any]:
    """Add a chamfer (beveled edge) feature to a body.

    Parameters
    ----------
    project:
        The project dictionary.
    body_index:
        Index of the target body.
    size:
        Chamfer size (distance).  Must be positive.
    edges:
        ``"all"`` to chamfer every edge, or a list of edge indices.

    Returns
    -------
    Dict[str, Any]
        The newly created chamfer feature dictionary.
    """
    _validate_project(project)
    body = _get_body(project, body_index)

    size = float(size)
    if size <= 0:
        raise ValueError(f"Chamfer size must be positive, got {size}")

    if edges != "all":
        if not isinstance(edges, (list, tuple)):
            raise ValueError("Edges must be 'all' or a list of edge indices")
        for idx in edges:
            if not isinstance(idx, int) or idx < 0:
                raise ValueError(
                    f"Edge index must be a non-negative integer, got {idx!r}"
                )
        edges = list(edges)

    if not body["features"]:
        raise ValueError("Cannot add chamfer to a body with no existing features")

    feature: Dict[str, Any] = {
        "id": _next_feature_id(body),
        "type": "chamfer",
        "size": size,
        "edges": edges,
    }

    body["features"].append(feature)
    return feature
