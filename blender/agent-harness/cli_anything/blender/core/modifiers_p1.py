# ruff: noqa: F403, F405, E501
from .modifiers_base import *  # noqa: F403


_MODIFIER_REGISTRY_PART0 = {
    "subdivision_surface": {
        "category": "generate",
        "description": "Subdivide mesh for smoother appearance",
        "bpy_type": "SUBSURF",
        "params": {
            "levels": {
                "type": "int",
                "default": 1,
                "min": 0,
                "max": 6,
                "description": "Subdivision levels for viewport",
            },
            "render_levels": {
                "type": "int",
                "default": 2,
                "min": 0,
                "max": 6,
                "description": "Subdivision levels for render",
            },
            "use_creases": {
                "type": "bool",
                "default": False,
                "description": "Use edge crease weights",
            },
        },
    },
    "mirror": {
        "category": "generate",
        "description": "Mirror mesh across an axis",
        "bpy_type": "MIRROR",
        "params": {
            "use_axis_x": {
                "type": "bool",
                "default": True,
                "description": "Mirror on X axis",
            },
            "use_axis_y": {
                "type": "bool",
                "default": False,
                "description": "Mirror on Y axis",
            },
            "use_axis_z": {
                "type": "bool",
                "default": False,
                "description": "Mirror on Z axis",
            },
            "use_clip": {
                "type": "bool",
                "default": True,
                "description": "Prevent vertices from crossing the mirror plane",
            },
            "merge_threshold": {
                "type": "float",
                "default": 0.001,
                "min": 0.0,
                "max": 1.0,
                "description": "Distance within which mirrored vertices are merged",
            },
        },
    },
    "array": {
        "category": "generate",
        "description": "Create array of object copies",
        "bpy_type": "ARRAY",
        "params": {
            "count": {
                "type": "int",
                "default": 2,
                "min": 1,
                "max": 1000,
                "description": "Number of array copies",
            },
            "relative_offset_x": {
                "type": "float",
                "default": 1.0,
                "min": -100.0,
                "max": 100.0,
                "description": "Relative offset on X axis",
            },
            "relative_offset_y": {
                "type": "float",
                "default": 0.0,
                "min": -100.0,
                "max": 100.0,
                "description": "Relative offset on Y axis",
            },
            "relative_offset_z": {
                "type": "float",
                "default": 0.0,
                "min": -100.0,
                "max": 100.0,
                "description": "Relative offset on Z axis",
            },
        },
    },
    "bevel": {
        "category": "generate",
        "description": "Bevel edges of mesh",
        "bpy_type": "BEVEL",
        "params": {
            "width": {
                "type": "float",
                "default": 0.1,
                "min": 0.0,
                "max": 100.0,
                "description": "Bevel width",
            },
            "segments": {
                "type": "int",
                "default": 1,
                "min": 1,
                "max": 100,
                "description": "Number of bevel segments",
            },
            "limit_method": {
                "type": "str",
                "default": "NONE",
                "description": "Limit method: NONE, ANGLE, WEIGHT, VGROUP",
            },
            "angle_limit": {
                "type": "float",
                "default": 0.523599,
                "min": 0.0,
                "max": 3.14159,
                "description": "Angle limit in radians (for ANGLE method)",
            },
        },
    },
}
