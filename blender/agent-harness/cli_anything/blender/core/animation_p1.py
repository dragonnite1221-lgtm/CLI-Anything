# ruff: noqa: F403, F405, E501
from .animation_base import *  # noqa: F403


def add_keyframe(
    project: Dict[str, Any],
    object_index: int,
    frame: int,
    prop: str,
    value: Any,
    interpolation: str = "BEZIER",
) -> Dict[str, Any]:
    """Add a keyframe to an object.

    Args:
        project: The scene dict
        object_index: Index of the target object
        frame: Frame number for the keyframe
        prop: Property to animate (location, rotation, scale, visible)
        value: Value at this keyframe
        interpolation: Interpolation type (CONSTANT, LINEAR, BEZIER)

    Returns:
        The new keyframe entry dict
    """
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(
            f"Object index {object_index} out of range (0-{len(objects) - 1})"
        )

    if prop not in ANIMATABLE_PROPERTIES:
        raise ValueError(
            f"Cannot animate property '{prop}'. Valid: {ANIMATABLE_PROPERTIES}"
        )

    interpolation = interpolation.upper()
    if interpolation not in INTERPOLATION_TYPES:
        raise ValueError(
            f"Invalid interpolation: {interpolation}. Valid: {INTERPOLATION_TYPES}"
        )

    scene = project.get("scene", {})
    if frame < scene.get("frame_start", 0):
        raise ValueError(
            f"Frame {frame} is before scene start ({scene.get('frame_start', 0)})"
        )

    # Parse the value based on property type
    if prop in ("location", "rotation", "scale"):
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if not isinstance(value, (list, tuple)) or len(value) != 3:
            raise ValueError(f"Property '{prop}' requires 3 components [x, y, z]")
        value = [float(x) for x in value]
    elif prop == "visible":
        value = str(value).lower() in ("true", "1", "yes")
    elif prop.startswith("material."):
        value = float(value)

    obj = objects[object_index]
    if "keyframes" not in obj:
        obj["keyframes"] = []

    # Check if keyframe already exists at this frame for this property
    for kf in obj["keyframes"]:
        if kf["frame"] == frame and kf["property"] == prop:
            kf["value"] = value
            kf["interpolation"] = interpolation
            return kf

    keyframe = {
        "frame": frame,
        "property": prop,
        "value": value,
        "interpolation": interpolation,
    }

    obj["keyframes"].append(keyframe)
    # Keep keyframes sorted by frame
    obj["keyframes"].sort(key=lambda k: (k["property"], k["frame"]))

    return keyframe


def remove_keyframe(
    project: Dict[str, Any],
    object_index: int,
    frame: int,
    prop: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Remove keyframe(s) from an object.

    Args:
        project: The scene dict
        object_index: Index of the target object
        frame: Frame number
        prop: Property name (if None, removes all keyframes at this frame)

    Returns:
        List of removed keyframes
    """
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(
            f"Object index {object_index} out of range (0-{len(objects) - 1})"
        )

    obj = objects[object_index]
    keyframes = obj.get("keyframes", [])

    removed = []
    remaining = []
    for kf in keyframes:
        if kf["frame"] == frame and (prop is None or kf["property"] == prop):
            removed.append(kf)
        else:
            remaining.append(kf)

    if not removed:
        raise ValueError(
            f"No keyframe found at frame {frame}"
            + (f" for property '{prop}'" if prop else "")
        )

    obj["keyframes"] = remaining
    return removed
