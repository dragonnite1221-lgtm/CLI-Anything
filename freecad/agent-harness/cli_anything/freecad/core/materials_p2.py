# ruff: noqa: F403, F405, E501
from .materials_base import *  # noqa: F403

# fmt: off
from .materials_p1 import _PRESETS_PART0  # noqa: E402,E501
# fmt: on


_PRESETS_PART1 = {
    "stainless_steel": {
        "color": [0.75, 0.75, 0.77, 1.0],
        "metallic": 0.95,
        "roughness": 0.2,
        "density": 8000,
        "youngs_modulus": 193,
        "poisson_ratio": 0.29,
        "yield_strength": 205,
        "ultimate_strength": 515,
    },
    "cast_iron": {
        "color": [0.4, 0.4, 0.42, 1.0],
        "metallic": 0.85,
        "roughness": 0.6,
        "density": 7200,
        "youngs_modulus": 170,
        "poisson_ratio": 0.26,
    },
    "carbon_fiber": {
        "color": [0.1, 0.1, 0.12, 1.0],
        "metallic": 0.3,
        "roughness": 0.15,
        "density": 1600,
        "youngs_modulus": 230,
    },
    "nylon": {
        "color": [0.9, 0.88, 0.82, 1.0],
        "metallic": 0.0,
        "roughness": 0.5,
        "density": 1150,
        "youngs_modulus": 2.7,
    },
    "abs": {
        "color": [0.95, 0.95, 0.9, 1.0],
        "metallic": 0.0,
        "roughness": 0.45,
        "density": 1040,
        "youngs_modulus": 2.3,
    },
    "pla": {
        "color": [0.9, 0.9, 0.85, 1.0],
        "metallic": 0.0,
        "roughness": 0.4,
        "density": 1240,
        "youngs_modulus": 3.5,
    },
    "petg": {
        "color": [0.85, 0.88, 0.92, 1.0],
        "metallic": 0.05,
        "roughness": 0.35,
        "density": 1270,
        "youngs_modulus": 2.2,
    },
    "concrete": {
        "color": [0.7, 0.7, 0.68, 1.0],
        "metallic": 0.0,
        "roughness": 0.9,
        "density": 2400,
        "youngs_modulus": 30,
    },
    "granite": {
        "color": [0.55, 0.5, 0.48, 1.0],
        "metallic": 0.1,
        "roughness": 0.7,
        "density": 2700,
        "youngs_modulus": 70,
    },
    "marble": {
        "color": [0.92, 0.9, 0.88, 1.0],
        "metallic": 0.05,
        "roughness": 0.3,
        "density": 2700,
        "youngs_modulus": 70,
    },
}
PRESETS: Dict[str, Dict[str, Any]] = {**_PRESETS_PART0, **_PRESETS_PART1}
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
