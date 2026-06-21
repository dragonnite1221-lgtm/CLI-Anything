# ruff: noqa: F403, F405, E501
from .body_base import *  # noqa: F403


def toggle_freeze(
    project: Dict[str, Any],
    body_index: int,
    feature_index: int,
) -> Dict[str, Any]:
    """Toggle the frozen state of a feature in a body (FreeCAD 1.1).

    Frozen features are excluded from recomputation.
    """
    bodies = project.get("bodies", [])
    if body_index < 0 or body_index >= len(bodies):
        raise IndexError(
            f"Body index {body_index} out of range (0..{len(bodies) - 1})."
        )
    body = bodies[body_index]
    features = body.get("features", [])
    if feature_index < 0 or feature_index >= len(features):
        raise IndexError(
            f"Feature index {feature_index} out of range (0..{len(features) - 1})."
        )
    feat = features[feature_index]
    feat["frozen"] = not feat.get("frozen", False)
    return feat
