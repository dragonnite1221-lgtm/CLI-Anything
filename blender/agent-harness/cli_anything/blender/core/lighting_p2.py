# ruff: noqa: F403, F405, E501
from .lighting_base import *  # noqa: F403


def set_camera(
    project: Dict[str, Any],
    index: int,
    prop: str,
    value: Any,
) -> None:
    """Set a camera property.

    Args:
        project: The scene dict
        index: Camera index
        prop: Property name
        value: New value
    """
    cameras = project.get("cameras", [])
    if index < 0 or index >= len(cameras):
        raise IndexError(f"Camera index {index} out of range (0-{len(cameras) - 1})")

    cam = cameras[index]
    valid_props = [
        "location",
        "rotation",
        "focal_length",
        "sensor_width",
        "clip_start",
        "clip_end",
        "type",
        "name",
        "dof_enabled",
        "dof_focus_distance",
        "dof_aperture",
    ]

    if prop not in valid_props:
        raise ValueError(f"Unknown camera property: {prop}. Valid: {valid_props}")

    if prop == "location":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Location must have 3 components")
        cam["location"] = [float(x) for x in value]
    elif prop == "rotation":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Rotation must have 3 components")
        cam["rotation"] = [float(x) for x in value]
    elif prop == "focal_length":
        val = float(value)
        if val <= 0:
            raise ValueError(f"Focal length must be positive: {val}")
        cam["focal_length"] = val
    elif prop == "sensor_width":
        val = float(value)
        if val <= 0:
            raise ValueError(f"Sensor width must be positive: {val}")
        cam["sensor_width"] = val
    elif prop == "clip_start":
        val = float(value)
        if val <= 0:
            raise ValueError(f"Clip start must be positive: {val}")
        cam["clip_start"] = val
    elif prop == "clip_end":
        cam["clip_end"] = float(value)
    elif prop == "type":
        if value not in CAMERA_TYPES:
            raise ValueError(f"Invalid camera type: {value}. Valid: {CAMERA_TYPES}")
        cam["type"] = value
    elif prop == "name":
        cam["name"] = str(value)
    elif prop == "dof_enabled":
        cam["dof_enabled"] = str(value).lower() in ("true", "1", "yes")
    elif prop == "dof_focus_distance":
        cam["dof_focus_distance"] = float(value)
    elif prop == "dof_aperture":
        cam["dof_aperture"] = float(value)


def set_active_camera(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Set the active camera by index."""
    cameras = project.get("cameras", [])
    if index < 0 or index >= len(cameras):
        raise IndexError(f"Camera index {index} out of range (0-{len(cameras) - 1})")

    for cam in cameras:
        cam["is_active"] = False
    cameras[index]["is_active"] = True

    return {
        "active_camera": cameras[index]["name"],
        "index": index,
    }


def get_camera(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Get a camera by index."""
    cameras = project.get("cameras", [])
    if index < 0 or index >= len(cameras):
        raise IndexError(f"Camera index {index} out of range (0-{len(cameras) - 1})")
    return cameras[index]


def list_cameras(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all cameras with summary info."""
    result = []
    for i, cam in enumerate(project.get("cameras", [])):
        result.append(
            {
                "index": i,
                "id": cam.get("id", i),
                "name": cam.get("name", f"Camera {i}"),
                "type": cam.get("type", "PERSP"),
                "location": cam.get("location", [0, 0, 5]),
                "rotation": cam.get("rotation", [0, 0, 0]),
                "focal_length": cam.get("focal_length", 50.0),
                "is_active": cam.get("is_active", False),
            }
        )
    return result
