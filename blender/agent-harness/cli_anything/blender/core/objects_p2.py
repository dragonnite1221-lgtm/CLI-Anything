# ruff: noqa: F403, F405, E501
from .objects_base import *  # noqa: F403


def transform_object(
    project: Dict[str, Any],
    index: int,
    translate: Optional[List[float]] = None,
    rotate: Optional[List[float]] = None,
    scale: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Apply a transform to an object.

    Args:
        project: The scene dict
        index: Object index
        translate: [dx, dy, dz] to add to current location
        rotate: [rx, ry, rz] in degrees to add to current rotation
        scale: [sx, sy, sz] to multiply with current scale
    """
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    obj = objects[index]

    if translate:
        if len(translate) != 3:
            raise ValueError(f"Translate must have 3 components, got {len(translate)}")
        obj["location"] = [obj["location"][i] + translate[i] for i in range(3)]
    if rotate:
        if len(rotate) != 3:
            raise ValueError(f"Rotate must have 3 components, got {len(rotate)}")
        obj["rotation"] = [obj["rotation"][i] + rotate[i] for i in range(3)]
    if scale:
        if len(scale) != 3:
            raise ValueError(f"Scale must have 3 components, got {len(scale)}")
        obj["scale"] = [obj["scale"][i] * scale[i] for i in range(3)]

    return obj


def set_object_property(
    project: Dict[str, Any], index: int, prop: str, value: Any
) -> None:
    """Set an object property."""
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")

    obj = objects[index]

    if prop == "name":
        obj["name"] = str(value)
    elif prop == "visible":
        obj["visible"] = str(value).lower() in ("true", "1", "yes")
    elif prop == "location":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Location must have 3 components")
        obj["location"] = [float(x) for x in value]
    elif prop == "rotation":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Rotation must have 3 components")
        obj["rotation"] = [float(x) for x in value]
    elif prop == "scale":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Scale must have 3 components")
        obj["scale"] = [float(x) for x in value]
    elif prop == "parent":
        # Set parent by object index or None
        if value is None or str(value).lower() == "none":
            obj["parent"] = None
        else:
            parent_idx = int(value)
            if parent_idx < 0 or parent_idx >= len(objects):
                raise IndexError(f"Parent index {parent_idx} out of range")
            if parent_idx == index:
                raise ValueError("Object cannot be its own parent")
            obj["parent"] = objects[parent_idx]["id"]
    else:
        raise ValueError(
            f"Unknown property: {prop}. Valid: name, visible, location, rotation, scale, parent"
        )


def get_object(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Get an object by index."""
    objects = project.get("objects", [])
    if index < 0 or index >= len(objects):
        raise IndexError(f"Object index {index} out of range (0-{len(objects) - 1})")
    return objects[index]


def list_objects(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all objects with summary info."""
    result = []
    for i, obj in enumerate(project.get("objects", [])):
        result.append(
            {
                "index": i,
                "id": obj.get("id", i),
                "name": obj.get("name", f"Object {i}"),
                "type": obj.get("type", "MESH"),
                "mesh_type": obj.get("mesh_type", "unknown"),
                "location": obj.get("location", [0, 0, 0]),
                "rotation": obj.get("rotation", [0, 0, 0]),
                "scale": obj.get("scale", [1, 1, 1]),
                "visible": obj.get("visible", True),
                "material": obj.get("material"),
                "modifier_count": len(obj.get("modifiers", [])),
                "keyframe_count": len(obj.get("keyframes", [])),
            }
        )
    return result
