# ruff: noqa: F403, F405, E501
from .lighting_base import *  # noqa: F403

# fmt: off
from .lighting_p1 import _next_light_id, _unique_light_name  # noqa: E402,E501
# fmt: on


def add_light(
    project: Dict[str, Any],
    light_type: str = "POINT",
    name: Optional[str] = None,
    location: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    color: Optional[List[float]] = None,
    power: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a light to the scene.

    Args:
        project: The scene dict
        light_type: POINT, SUN, SPOT, or AREA
        name: Light name
        location: [x, y, z] position
        rotation: [x, y, z] rotation in degrees
        color: [R, G, B] color (0.0-1.0)
        power: Light power/energy (watts for point/spot/area, unitless for sun)

    Returns:
        The new light dict
    """
    light_type = light_type.upper()
    if light_type not in LIGHT_TYPES:
        raise ValueError(
            f"Invalid light type: {light_type}. Valid: {list(LIGHT_TYPES.keys())}"
        )

    if location is not None and len(location) != 3:
        raise ValueError(f"Location must have 3 components, got {len(location)}")
    if rotation is not None and len(rotation) != 3:
        raise ValueError(f"Rotation must have 3 components, got {len(rotation)}")
    if color is not None:
        if len(color) != 3:
            raise ValueError(
                f"Color must have 3 components [R, G, B], got {len(color)}"
            )
        for i, c in enumerate(color):
            if not 0.0 <= c <= 1.0:
                raise ValueError(f"Color component {i} must be 0.0-1.0, got {c}")
    if power is not None and power < 0:
        raise ValueError(f"Power must be non-negative: {power}")

    defaults = LIGHT_TYPES[light_type]
    light_name = _unique_light_name(project, name or light_type.capitalize())

    light = {
        "id": _next_light_id(project),
        "name": light_name,
        "type": light_type,
        "location": list(location) if location else [0.0, 0.0, 3.0],
        "rotation": list(rotation) if rotation else [0.0, 0.0, 0.0],
        "color": list(color) if color else list(defaults["color"]),
        "power": power if power is not None else defaults["power"],
    }

    # Add type-specific properties
    if light_type == "POINT":
        light["radius"] = defaults["radius"]
    elif light_type == "SUN":
        light["angle"] = defaults["angle"]
    elif light_type == "SPOT":
        light["radius"] = defaults["radius"]
        light["spot_size"] = defaults["spot_size"]
        light["spot_blend"] = defaults["spot_blend"]
    elif light_type == "AREA":
        light["size"] = defaults["size"]
        light["size_y"] = defaults["size_y"]
        light["shape"] = defaults["shape"]

    if "lights" not in project:
        project["lights"] = []
    project["lights"].append(light)

    return light
