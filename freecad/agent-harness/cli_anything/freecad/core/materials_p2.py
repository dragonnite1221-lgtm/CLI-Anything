# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403


MATERIAL_PROPS: Dict[str, Dict[str, Any]] = {
    "color": {"type": "color4", "description": "Base color [R, G, B, A] (0.0-1.0)"},
    "metallic": {
        "type": "float",
        "min": 0.0,
        "max": 1.0,
        "description": "Metallic factor",
    },
    "roughness": {
        "type": "float",
        "min": 0.0,
        "max": 1.0,
        "description": "Roughness factor",
    },
    "name": {"type": "str", "description": "Material display name"},
    "density": {"type": "float", "min": 0.0, "description": "Density (kg/m^3)"},
    "youngs_modulus": {
        "type": "float",
        "min": 0.0,
        "description": "Young's modulus (GPa)",
    },
    "poisson_ratio": {
        "type": "float",
        "min": 0.0,
        "max": 0.5,
        "description": "Poisson's ratio",
    },
    "thermal_conductivity": {
        "type": "float",
        "min": 0.0,
        "description": "Thermal conductivity (W/(m*K))",
    },
    "specific_heat": {
        "type": "float",
        "min": 0.0,
        "description": "Specific heat capacity (J/(kg*K))",
    },
    "yield_strength": {
        "type": "float",
        "min": 0.0,
        "description": "Yield strength (MPa)",
    },
    "ultimate_strength": {
        "type": "float",
        "min": 0.0,
        "description": "Ultimate tensile strength (MPa)",
    },
}


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


def _validate_project(project: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if *project* is not a valid dict with a materials list."""
    if not isinstance(project, dict):
        raise ValueError("Project must be a dictionary")
    if "materials" not in project:
        raise ValueError("Project is missing 'materials' collection")
    if not isinstance(project["materials"], list):
        raise ValueError("Project 'materials' must be a list")


def _get_material(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Return material at *index* or raise ``IndexError``."""
    materials = project["materials"]
    if index < 0 or index >= len(materials):
        raise IndexError(
            f"Material index {index} out of range (0-{len(materials) - 1})"
        )
    return materials[index]


def _validate_color(color: List[float]) -> List[float]:
    """Validate and return a color as a list of 4 floats in [0, 1]."""
    if not isinstance(color, (list, tuple)):
        raise ValueError(f"Color must be a list, got {type(color).__name__}")
    if len(color) < 3:
        raise ValueError(
            f"Color must have at least 3 components [R, G, B], got {len(color)}"
        )
    if len(color) == 3:
        color = list(color) + [1.0]
    if len(color) > 4:
        raise ValueError(
            f"Color must have at most 4 components [R, G, B, A], got {len(color)}"
        )
    result: List[float] = []
    for i, c in enumerate(color):
        try:
            val = float(c)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Color component {i} must be numeric: {exc}") from exc
        if not 0.0 <= val <= 1.0:
            raise ValueError(f"Color component {i} must be 0.0-1.0, got {val}")
        result.append(val)
    return result
