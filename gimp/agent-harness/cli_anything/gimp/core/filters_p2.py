# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART1 = {
    "solarize": {
        "category": "adjustment",
        "description": "Solarize effect",
        "params": {
            "threshold": {
                "type": "int",
                "default": 128,
                "min": 0,
                "max": 255,
                "description": "Threshold for inversion",
            }
        },
        "engine": "pillow_ops",
        "pillow_func": "solarize",
    },
    "grayscale": {
        "category": "adjustment",
        "description": "Convert to grayscale",
        "params": {},
        "engine": "pillow_ops",
        "pillow_func": "grayscale",
    },
    "sepia": {
        "category": "adjustment",
        "description": "Apply sepia tone",
        "params": {
            "strength": {
                "type": "float",
                "default": 0.8,
                "min": 0.0,
                "max": 1.0,
                "description": "Sepia effect strength",
            }
        },
        "engine": "custom",
        "custom_func": "apply_sepia",
    },
    "gaussian_blur": {
        "category": "blur",
        "description": "Gaussian blur",
        "params": {
            "radius": {
                "type": "float",
                "default": 2.0,
                "min": 0.1,
                "max": 100.0,
                "description": "Blur radius in pixels",
            }
        },
        "engine": "pillow_filter",
        "pillow_filter": "GaussianBlur",
    },
    "box_blur": {
        "category": "blur",
        "description": "Box blur (uniform average)",
        "params": {
            "radius": {
                "type": "float",
                "default": 2.0,
                "min": 0.1,
                "max": 100.0,
                "description": "Blur radius in pixels",
            }
        },
        "engine": "pillow_filter",
        "pillow_filter": "BoxBlur",
    },
    "unsharp_mask": {
        "category": "blur",
        "description": "Unsharp mask (sharpen via blur)",
        "params": {
            "radius": {
                "type": "float",
                "default": 2.0,
                "min": 0.1,
                "max": 100.0,
                "description": "Blur radius",
            },
            "percent": {
                "type": "int",
                "default": 150,
                "min": 1,
                "max": 500,
                "description": "Sharpening strength percent",
            },
            "threshold": {
                "type": "int",
                "default": 3,
                "min": 0,
                "max": 255,
                "description": "Minimum brightness change to sharpen",
            },
        },
        "engine": "pillow_filter",
        "pillow_filter": "UnsharpMask",
    },
    "smooth": {
        "category": "blur",
        "description": "Smooth (reduce noise)",
        "params": {},
        "engine": "pillow_filter",
        "pillow_filter": "SMOOTH_MORE",
    },
    "find_edges": {
        "category": "stylize",
        "description": "Edge detection",
        "params": {},
        "engine": "pillow_filter",
        "pillow_filter": "FIND_EDGES",
    },
}
