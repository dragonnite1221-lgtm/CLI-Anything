# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403


def set_material_property(
    project: Dict[str, Any],
    index: int,
    prop: str,
    value: Any,
) -> None:
    """Set a material property.

    Args:
        project: The scene dict
        index: Material index
        prop: Property name
        value: New value
    """
    materials = project.get("materials", [])
    if index < 0 or index >= len(materials):
        raise IndexError(
            f"Material index {index} out of range (0-{len(materials) - 1})"
        )

    mat = materials[index]

    if prop not in MATERIAL_PROPS:
        raise ValueError(
            f"Unknown material property: {prop}. Valid: {list(MATERIAL_PROPS.keys())}"
        )

    spec = MATERIAL_PROPS[prop]
    ptype = spec["type"]

    if ptype == "float":
        value = float(value)
        if "min" in spec and value < spec["min"]:
            raise ValueError(f"Property '{prop}' minimum is {spec['min']}, got {value}")
        if "max" in spec and value > spec["max"]:
            raise ValueError(f"Property '{prop}' maximum is {spec['max']}, got {value}")
        mat[prop] = value
    elif ptype == "color4":
        if isinstance(value, str):
            value = [float(x) for x in value.split(",")]
        if len(value) < 3:
            raise ValueError(f"Color must have at least 3 components, got {len(value)}")
        if len(value) == 3:
            value = list(value) + [1.0]
        for i, c in enumerate(value):
            if not 0.0 <= float(c) <= 1.0:
                raise ValueError(f"Color component {i} must be 0.0-1.0, got {c}")
        mat[prop] = [float(x) for x in value]
    elif ptype == "bool":
        mat[prop] = str(value).lower() in ("true", "1", "yes")
    else:
        mat[prop] = value


def get_material(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Get a material by index."""
    materials = project.get("materials", [])
    if index < 0 or index >= len(materials):
        raise IndexError(
            f"Material index {index} out of range (0-{len(materials) - 1})"
        )
    return materials[index]


def list_materials(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all materials with summary info."""
    result = []
    for i, mat in enumerate(project.get("materials", [])):
        result.append(
            {
                "index": i,
                "id": mat.get("id", i),
                "name": mat.get("name", f"Material {i}"),
                "type": mat.get("type", "principled"),
                "color": mat.get("color", [0.8, 0.8, 0.8, 1.0]),
                "metallic": mat.get("metallic", 0.0),
                "roughness": mat.get("roughness", 0.5),
                "specular": mat.get("specular", 0.5),
            }
        )
    return result
