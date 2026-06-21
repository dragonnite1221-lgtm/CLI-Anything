# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p1 import _FILTER_REGISTRY_PART0  # noqa: E402,E501
from .filters_p2 import _FILTER_REGISTRY_PART1  # noqa: E402,E501
# fmt: on


_FILTER_REGISTRY_PART2 = {
    "emboss": {
        "category": "stylize",
        "description": "Emboss effect",
        "params": {},
        "engine": "pillow_filter",
        "pillow_filter": "EMBOSS",
    },
    "contour": {
        "category": "stylize",
        "description": "Contour tracing",
        "params": {},
        "engine": "pillow_filter",
        "pillow_filter": "CONTOUR",
    },
    "detail": {
        "category": "stylize",
        "description": "Enhance detail",
        "params": {},
        "engine": "pillow_filter",
        "pillow_filter": "DETAIL",
    },
    "rotate": {
        "category": "transform",
        "description": "Rotate layer",
        "params": {
            "angle": {
                "type": "float",
                "default": 0.0,
                "min": -360.0,
                "max": 360.0,
                "description": "Rotation angle in degrees",
            },
            "expand": {
                "type": "bool",
                "default": True,
                "description": "Expand canvas to fit rotated image",
            },
        },
        "engine": "pillow_transform",
        "pillow_method": "rotate",
    },
    "flip_h": {
        "category": "transform",
        "description": "Flip horizontally",
        "params": {},
        "engine": "pillow_transform",
        "pillow_method": "flip_h",
    },
    "flip_v": {
        "category": "transform",
        "description": "Flip vertically",
        "params": {},
        "engine": "pillow_transform",
        "pillow_method": "flip_v",
    },
    "resize": {
        "category": "transform",
        "description": "Resize layer",
        "params": {
            "width": {
                "type": "int",
                "default": 0,
                "min": 1,
                "max": 65535,
                "description": "Target width",
            },
            "height": {
                "type": "int",
                "default": 0,
                "min": 1,
                "max": 65535,
                "description": "Target height",
            },
            "resample": {
                "type": "str",
                "default": "lanczos",
                "description": "Resampling: nearest, bilinear, bicubic, lanczos",
            },
        },
        "engine": "pillow_transform",
        "pillow_method": "resize",
    },
    "crop": {
        "category": "transform",
        "description": "Crop layer",
        "params": {
            "left": {"type": "int", "default": 0, "min": 0, "max": 65535},
            "top": {"type": "int", "default": 0, "min": 0, "max": 65535},
            "right": {"type": "int", "default": 0, "min": 0, "max": 65535},
            "bottom": {"type": "int", "default": 0, "min": 0, "max": 65535},
        },
        "engine": "pillow_transform",
        "pillow_method": "crop",
    },
}
FILTER_REGISTRY = {
    **_FILTER_REGISTRY_PART0,
    **_FILTER_REGISTRY_PART1,
    **_FILTER_REGISTRY_PART2,
}


def list_available(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available filters, optionally filtered by category."""
    result = []
    for name, info in FILTER_REGISTRY.items():
        if category and info["category"] != category:
            continue
        result.append(
            {
                "name": name,
                "category": info["category"],
                "description": info["description"],
                "param_count": len(info["params"]),
            }
        )
    return result
