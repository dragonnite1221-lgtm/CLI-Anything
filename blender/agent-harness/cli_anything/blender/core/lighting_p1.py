# ruff: noqa: F403, F405, E501
from .lighting_base import *  # noqa: F403


def _next_camera_id(project: Dict[str, Any]) -> int:
    cameras = project.get("cameras", [])
    existing_ids = [c.get("id", 0) for c in cameras]
    return max(existing_ids, default=-1) + 1


def _next_light_id(project: Dict[str, Any]) -> int:
    lights = project.get("lights", [])
    existing_ids = [l.get("id", 0) for l in lights]
    return max(existing_ids, default=-1) + 1


def _unique_camera_name(project: Dict[str, Any], base_name: str) -> str:
    cameras = project.get("cameras", [])
    existing_names = {c.get("name", "") for c in cameras}
    if base_name not in existing_names:
        return base_name
    counter = 1
    while f"{base_name}.{counter:03d}" in existing_names:
        counter += 1
    return f"{base_name}.{counter:03d}"


def _unique_light_name(project: Dict[str, Any], base_name: str) -> str:
    lights = project.get("lights", [])
    existing_names = {l.get("name", "") for l in lights}
    if base_name not in existing_names:
        return base_name
    counter = 1
    while f"{base_name}.{counter:03d}" in existing_names:
        counter += 1
    return f"{base_name}.{counter:03d}"


def add_camera(
    project: Dict[str, Any],
    name: Optional[str] = None,
    location: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    camera_type: str = "PERSP",
    focal_length: float = 50.0,
    sensor_width: float = 36.0,
    clip_start: float = 0.1,
    clip_end: float = 1000.0,
    set_active: bool = False,
) -> Dict[str, Any]:
    """Add a camera to the scene.

    Args:
        project: The scene dict
        name: Camera name
        location: [x, y, z] position
        rotation: [x, y, z] rotation in degrees
        camera_type: PERSP, ORTHO, or PANO
        focal_length: Lens focal length in mm
        sensor_width: Camera sensor width in mm
        clip_start: Near clipping distance
        clip_end: Far clipping distance
        set_active: Whether to set this as the active camera

    Returns:
        The new camera dict
    """
    if camera_type not in CAMERA_TYPES:
        raise ValueError(f"Invalid camera type: {camera_type}. Valid: {CAMERA_TYPES}")
    if focal_length <= 0:
        raise ValueError(f"Focal length must be positive: {focal_length}")
    if clip_start <= 0:
        raise ValueError(f"Clip start must be positive: {clip_start}")
    if clip_end <= clip_start:
        raise ValueError(
            f"Clip end ({clip_end}) must be greater than clip start ({clip_start})"
        )
    if location is not None and len(location) != 3:
        raise ValueError(f"Location must have 3 components, got {len(location)}")
    if rotation is not None and len(rotation) != 3:
        raise ValueError(f"Rotation must have 3 components, got {len(rotation)}")

    cam_name = _unique_camera_name(project, name or "Camera")

    camera = {
        "id": _next_camera_id(project),
        "name": cam_name,
        "type": camera_type,
        "location": list(location) if location else [0.0, 0.0, 5.0],
        "rotation": list(rotation) if rotation else [0.0, 0.0, 0.0],
        "focal_length": focal_length,
        "sensor_width": sensor_width,
        "clip_start": clip_start,
        "clip_end": clip_end,
        "dof_enabled": False,
        "dof_focus_distance": 10.0,
        "dof_aperture": 2.8,
        "is_active": False,
    }

    if "cameras" not in project:
        project["cameras"] = []
    project["cameras"].append(camera)

    if set_active or len(project["cameras"]) == 1:
        # Set as active camera (deactivate others)
        for cam in project["cameras"]:
            cam["is_active"] = False
        camera["is_active"] = True

    return camera
