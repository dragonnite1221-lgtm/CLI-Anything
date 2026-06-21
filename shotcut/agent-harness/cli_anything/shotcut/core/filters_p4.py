# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART3 = {
    "gamma": {
        "service": "frei0r.gamma",
        "category": "video",
        "description": "Gamma correction",
        "params": {
            "gamma": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-5.0",
                "description": "Gamma value (1.0 = neutral)",
            },
        },
    },
    "color-temperature": {
        "service": "frei0r.colortap",
        "category": "video",
        "description": "Color temperature (warm/cool tint)",
        "params": {
            "table": {
                "type": "string",
                "default": "0",
                "description": "Color preset table index",
            },
        },
    },
    "lut3d": {
        "service": "avfilter.lut3d",
        "category": "video",
        "description": "Apply 3D LUT color grading file (.cube, .3dl)",
        "params": {
            "av.file": {
                "type": "string",
                "default": "",
                "description": "Path to .cube or .3dl LUT file",
            },
        },
    },
    "vibrance": {
        "service": "frei0r.colgate",
        "category": "video",
        "description": "Vibrance (intelligent saturation boost)",
        "params": {
            "neutral_color": {
                "type": "string",
                "default": "0.5 0.5 0.5",
                "description": "Neutral reference color",
            },
            "color_temperature": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Color temperature shift",
            },
        },
    },
    "invert": {
        "service": "frei0r.invert0r",
        "category": "video",
        "description": "Invert colors (negative)",
        "params": {},
    },
    "grayscale": {
        "service": "greyscale",
        "category": "video",
        "description": "Convert to grayscale",
        "params": {},
    },
    "threshold": {
        "service": "frei0r.threshold0r",
        "category": "video",
        "description": "Threshold (convert to black and white based on level)",
        "params": {
            "threshold": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Threshold level",
            },
        },
    },
    "posterize": {
        "service": "frei0r.posterize",
        "category": "video",
        "description": "Reduce color palette (posterization)",
        "params": {
            "levels": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Number of color levels (normalized)",
            },
        },
    },
}
