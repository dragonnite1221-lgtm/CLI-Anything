# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403


def _next_id(project: Dict[str, Any]) -> int:
    """Generate the next unique material ID."""
    materials = project.get("materials", [])
    existing_ids = [m.get("id", 0) for m in materials]
    return max(existing_ids, default=-1) + 1


def _unique_name(project: Dict[str, Any], base_name: str) -> str:
    """Generate a unique material name."""
    materials = project.get("materials", [])
    existing_names = {m.get("name", "") for m in materials}
    if base_name not in existing_names:
        return base_name
    counter = 1
    while f"{base_name}.{counter:03d}" in existing_names:
        counter += 1
    return f"{base_name}.{counter:03d}"


def create_material(
    project: Dict[str, Any],
    name: str = "Material",
    color: Optional[List[float]] = None,
    metallic: float = 0.0,
    roughness: float = 0.5,
    specular: float = 0.5,
) -> Dict[str, Any]:
    """Create a new Principled BSDF material.

    Args:
        project: The scene dict
        name: Material name
        color: Base color [R, G, B, A] (0.0-1.0 each)
        metallic: Metallic factor (0.0-1.0)
        roughness: Roughness factor (0.0-1.0)
        specular: Specular factor (0.0-2.0)

    Returns:
        The new material dict
    """
    if color is not None:
        if len(color) < 3:
            raise ValueError(
                f"Color must have at least 3 components [R, G, B], got {len(color)}"
            )
        if len(color) == 3:
            color = list(color) + [1.0]
        for i, c in enumerate(color):
            if not 0.0 <= c <= 1.0:
                raise ValueError(f"Color component {i} must be 0.0-1.0, got {c}")

    if not 0.0 <= metallic <= 1.0:
        raise ValueError(f"Metallic must be 0.0-1.0, got {metallic}")
    if not 0.0 <= roughness <= 1.0:
        raise ValueError(f"Roughness must be 0.0-1.0, got {roughness}")
    if not 0.0 <= specular <= 2.0:
        raise ValueError(f"Specular must be 0.0-2.0, got {specular}")

    mat_name = _unique_name(project, name)

    mat = {
        "id": _next_id(project),
        "name": mat_name,
        "type": "principled",
        "color": color if color else list(DEFAULT_MATERIAL["color"]),
        "metallic": metallic,
        "roughness": roughness,
        "specular": specular,
        "emission_color": list(DEFAULT_MATERIAL["emission_color"]),
        "emission_strength": 0.0,
        "alpha": 1.0,
        "use_backface_culling": False,
    }

    if "materials" not in project:
        project["materials"] = []
    project["materials"].append(mat)

    return mat


def assign_material(
    project: Dict[str, Any],
    material_index: int,
    object_index: int,
) -> Dict[str, Any]:
    """Assign a material to an object.

    Args:
        project: The scene dict
        material_index: Index of the material
        object_index: Index of the object

    Returns:
        Dict with assignment info
    """
    materials = project.get("materials", [])
    objects = project.get("objects", [])

    if material_index < 0 or material_index >= len(materials):
        raise IndexError(
            f"Material index {material_index} out of range (0-{len(materials) - 1})"
        )
    if object_index < 0 or object_index >= len(objects):
        raise IndexError(
            f"Object index {object_index} out of range (0-{len(objects) - 1})"
        )

    mat = materials[material_index]
    obj = objects[object_index]
    obj["material"] = mat["id"]

    return {
        "material": mat["name"],
        "material_id": mat["id"],
        "object": obj["name"],
        "object_id": obj["id"],
    }
