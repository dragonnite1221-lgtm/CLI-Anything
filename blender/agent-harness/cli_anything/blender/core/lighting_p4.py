# ruff: noqa: F403, F405, E501
from .lighting_base import *  # noqa: F403


def set_light(
    project: Dict[str, Any],
    index: int,
    prop: str,
    value: Any,
) -> None:
    """Set a light property.

    Args:
        project: The scene dict
        index: Light index
        prop: Property name
        value: New value
    """
    lights = project.get("lights", [])
    if index < 0 or index >= len(lights):
        raise IndexError(f"Light index {index} out of range (0-{len(lights) - 1})")

    light = lights[index]
    valid_props = [
        "location",
        "rotation",
        "color",
        "power",
        "name",
        "radius",
        "angle",
        "spot_size",
        "spot_blend",
        "size",
        "size_y",
        "shape",
    ]

    if prop not in valid_props:
        raise ValueError(f"Unknown light property: {prop}. Valid: {valid_props}")

    if prop == "location":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Location must have 3 components")
        light["location"] = [float(x) for x in value]
    elif prop == "rotation":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Rotation must have 3 components")
        light["rotation"] = [float(x) for x in value]
    elif prop == "color":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) != 3:
            raise ValueError("Color must have 3 components [R, G, B]")
        for i, c in enumerate(value):
            if not 0.0 <= float(c) <= 1.0:
                raise ValueError(f"Color component {i} must be 0.0-1.0, got {c}")
        light["color"] = [float(x) for x in value]
    elif prop == "power":
        val = float(value)
        if val < 0:
            raise ValueError(f"Power must be non-negative: {val}")
        light["power"] = val
    elif prop == "name":
        light["name"] = str(value)
    elif prop in ("radius", "angle", "spot_size", "spot_blend", "size", "size_y"):
        light[prop] = float(value)
    elif prop == "shape":
        if value not in ("RECTANGLE", "SQUARE", "DISK", "ELLIPSE"):
            raise ValueError(
                f"Invalid shape: {value}. Valid: RECTANGLE, SQUARE, DISK, ELLIPSE"
            )
        light["shape"] = value


def get_light(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Get a light by index."""
    lights = project.get("lights", [])
    if index < 0 or index >= len(lights):
        raise IndexError(f"Light index {index} out of range (0-{len(lights) - 1})")
    return lights[index]


def list_lights(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all lights with summary info."""
    result = []
    for i, light in enumerate(project.get("lights", [])):
        result.append(
            {
                "index": i,
                "id": light.get("id", i),
                "name": light.get("name", f"Light {i}"),
                "type": light.get("type", "POINT"),
                "location": light.get("location", [0, 0, 3]),
                "color": light.get("color", [1, 1, 1]),
                "power": light.get("power", 1000),
            }
        )
    return result
