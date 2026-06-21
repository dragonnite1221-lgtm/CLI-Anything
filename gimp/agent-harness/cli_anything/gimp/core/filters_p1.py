# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART0 = {
    "brightness": {
        "category": "adjustment",
        "description": "Adjust image brightness",
        "params": {
            "factor": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 10.0,
                "description": "1.0=neutral, >1=brighter, <1=darker",
            }
        },
        "engine": "pillow_enhance",
        "pillow_class": "Brightness",
    },
    "contrast": {
        "category": "adjustment",
        "description": "Adjust image contrast",
        "params": {
            "factor": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 10.0,
                "description": "1.0=neutral, >1=more contrast",
            }
        },
        "engine": "pillow_enhance",
        "pillow_class": "Contrast",
    },
    "saturation": {
        "category": "adjustment",
        "description": "Adjust color saturation",
        "params": {
            "factor": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 10.0,
                "description": "1.0=neutral, 0=grayscale, >1=vivid",
            }
        },
        "engine": "pillow_enhance",
        "pillow_class": "Color",
    },
    "sharpness": {
        "category": "adjustment",
        "description": "Adjust image sharpness",
        "params": {
            "factor": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 10.0,
                "description": "1.0=neutral, >1=sharper, 0=blurred",
            }
        },
        "engine": "pillow_enhance",
        "pillow_class": "Sharpness",
    },
    "autocontrast": {
        "category": "adjustment",
        "description": "Automatic contrast stretch",
        "params": {
            "cutoff": {
                "type": "float",
                "default": 0.0,
                "min": 0.0,
                "max": 49.0,
                "description": "Percent of lightest/darkest pixels to clip",
            }
        },
        "engine": "pillow_ops",
        "pillow_func": "autocontrast",
    },
    "equalize": {
        "category": "adjustment",
        "description": "Equalize histogram",
        "params": {},
        "engine": "pillow_ops",
        "pillow_func": "equalize",
    },
    "invert": {
        "category": "adjustment",
        "description": "Invert colors (negative)",
        "params": {},
        "engine": "pillow_ops",
        "pillow_func": "invert",
    },
    "posterize": {
        "category": "adjustment",
        "description": "Reduce color depth (posterize)",
        "params": {
            "bits": {
                "type": "int",
                "default": 4,
                "min": 1,
                "max": 8,
                "description": "Bits per channel (fewer = more posterized)",
            }
        },
        "engine": "pillow_ops",
        "pillow_func": "posterize",
    },
}
