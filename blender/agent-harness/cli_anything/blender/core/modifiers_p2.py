# ruff: noqa: F403, F405, E501
from .modifiers_base import *  # noqa: F403

# fmt: off
from .modifiers_p1 import _MODIFIER_REGISTRY_PART0  # noqa: E402,E501
# fmt: on


_MODIFIER_REGISTRY_PART1 = {
    "solidify": {
        "category": "generate",
        "description": "Add thickness to mesh surface",
        "bpy_type": "SOLIDIFY",
        "params": {
            "thickness": {
                "type": "float",
                "default": 0.01,
                "min": -10.0,
                "max": 10.0,
                "description": "Thickness of solidified surface",
            },
            "offset": {
                "type": "float",
                "default": -1.0,
                "min": -1.0,
                "max": 1.0,
                "description": "Offset direction (-1=outward, 1=inward)",
            },
            "use_even_offset": {
                "type": "bool",
                "default": False,
                "description": "Maintain even thickness",
            },
        },
    },
    "decimate": {
        "category": "generate",
        "description": "Reduce polygon count",
        "bpy_type": "DECIMATE",
        "params": {
            "ratio": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0,
                "description": "Ratio of faces to keep",
            },
            "decimate_type": {
                "type": "str",
                "default": "COLLAPSE",
                "description": "Method: COLLAPSE, UNSUBDIV, DISSOLVE",
            },
        },
    },
    "boolean": {
        "category": "generate",
        "description": "Boolean operation with another object",
        "bpy_type": "BOOLEAN",
        "params": {
            "operation": {
                "type": "str",
                "default": "DIFFERENCE",
                "description": "Operation: DIFFERENCE, UNION, INTERSECT",
            },
            "operand_object": {
                "type": "str",
                "default": "",
                "description": "Name of the operand object",
            },
            "solver": {
                "type": "str",
                "default": "EXACT",
                "description": "Solver: EXACT, FAST",
            },
        },
    },
    "smooth": {
        "category": "deform",
        "description": "Smooth mesh vertices",
        "bpy_type": "SMOOTH",
        "params": {
            "factor": {
                "type": "float",
                "default": 0.5,
                "min": -10.0,
                "max": 10.0,
                "description": "Smoothing factor",
            },
            "iterations": {
                "type": "int",
                "default": 1,
                "min": 0,
                "max": 1000,
                "description": "Number of smoothing iterations",
            },
            "use_x": {
                "type": "bool",
                "default": True,
                "description": "Smooth on X axis",
            },
            "use_y": {
                "type": "bool",
                "default": True,
                "description": "Smooth on Y axis",
            },
            "use_z": {
                "type": "bool",
                "default": True,
                "description": "Smooth on Z axis",
            },
        },
    },
}
MODIFIER_REGISTRY = {**_MODIFIER_REGISTRY_PART0, **_MODIFIER_REGISTRY_PART1}


def list_available(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available modifiers, optionally filtered by category."""
    result = []
    for name, info in MODIFIER_REGISTRY.items():
        if category and info["category"] != category:
            continue
        result.append(
            {
                "name": name,
                "category": info["category"],
                "description": info["description"],
                "bpy_type": info["bpy_type"],
                "param_count": len(info["params"]),
            }
        )
    return result


def get_modifier_info(name: str) -> Dict[str, Any]:
    """Get detailed info about a modifier type."""
    if name not in MODIFIER_REGISTRY:
        raise ValueError(
            f"Unknown modifier: {name}. Use 'modifier list-available' to see options."
        )
    info = MODIFIER_REGISTRY[name]
    return {
        "name": name,
        "category": info["category"],
        "description": info["description"],
        "bpy_type": info["bpy_type"],
        "params": info["params"],
    }
