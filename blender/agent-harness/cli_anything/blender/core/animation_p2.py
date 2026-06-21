# ruff: noqa: F403, F405, E501
from .animation_base import *  # noqa: F403


def set_frame_range(
    project: Dict[str, Any],
    frame_start: int,
    frame_end: int,
) -> Dict[str, Any]:
    """Set the animation frame range.

    Args:
        project: The scene dict
        frame_start: First frame
        frame_end: Last frame

    Returns:
        Dict with old and new range
    """
    if frame_start < 0:
        raise ValueError(f"Frame start must be non-negative: {frame_start}")
    if frame_end < frame_start:
        raise ValueError(
            f"Frame end ({frame_end}) must be >= frame start ({frame_start})"
        )

    scene = project.get("scene", {})
    old_start = scene.get("frame_start", 1)
    old_end = scene.get("frame_end", 250)

    scene["frame_start"] = frame_start
    scene["frame_end"] = frame_end

    # Clamp current frame to new range
    current = scene.get("frame_current", frame_start)
    if current < frame_start:
        scene["frame_current"] = frame_start
    elif current > frame_end:
        scene["frame_current"] = frame_end

    return {
        "old_range": f"{old_start}-{old_end}",
        "new_range": f"{frame_start}-{frame_end}",
    }


def set_fps(project: Dict[str, Any], fps: int) -> Dict[str, Any]:
    """Set the animation FPS (frames per second).

    Args:
        project: The scene dict
        fps: Target FPS

    Returns:
        Dict with old and new FPS
    """
    if fps < 1:
        raise ValueError(f"FPS must be positive: {fps}")

    scene = project.get("scene", {})
    old_fps = scene.get("fps", 24)
    scene["fps"] = fps

    return {
        "old_fps": old_fps,
        "new_fps": fps,
    }


def set_current_frame(project: Dict[str, Any], frame: int) -> Dict[str, Any]:
    """Set the current frame.

    Args:
        project: The scene dict
        frame: Frame number

    Returns:
        Dict with old and new frame
    """
    scene = project.get("scene", {})
    old_frame = scene.get("frame_current", 1)
    frame_start = scene.get("frame_start", 0)
    frame_end = scene.get("frame_end", 250)

    if frame < frame_start or frame > frame_end:
        raise ValueError(f"Frame {frame} is outside range [{frame_start}, {frame_end}]")

    scene["frame_current"] = frame

    return {
        "old_frame": old_frame,
        "new_frame": frame,
    }


def list_keyframes(
    project: Dict[str, Any],
    object_index: int,
    prop: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List keyframes for an object.

    Args:
        project: The scene dict
        object_index: Index of the target object
        prop: Filter by property name (optional)

    Returns:
        List of keyframe dicts
    """
    objects = project.get("objects", [])
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(
            f"Object index {object_index} out of range (0-{len(objects) - 1})"
        )

    obj = objects[object_index]
    keyframes = obj.get("keyframes", [])

    result = []
    for kf in keyframes:
        if prop is None or kf["property"] == prop:
            result.append(
                {
                    "frame": kf["frame"],
                    "property": kf["property"],
                    "value": kf["value"],
                    "interpolation": kf.get("interpolation", "BEZIER"),
                }
            )

    return result
