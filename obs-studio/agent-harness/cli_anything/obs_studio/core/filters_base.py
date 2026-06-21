# ruff: noqa: E501
"""OBS Studio CLI - Filter management."""

import copy
from typing import Dict, Any, List, Optional
from cli_anything.obs_studio.utils.obs_utils import (
    generate_id,
    unique_name,
    get_item,
    validate_range,
)


FILTER_TYPES = {
    "color_correction": {
        "label": "Color Correction",
        "category": "video",
        "params": {
            "gamma": {"type": "float", "default": 0.0, "min": -3.0, "max": 3.0},
            "contrast": {"type": "float", "default": 0.0, "min": -4.0, "max": 4.0},
            "brightness": {"type": "float", "default": 0.0, "min": -1.0, "max": 1.0},
            "saturation": {"type": "float", "default": 0.0, "min": -1.0, "max": 5.0},
            "hue_shift": {"type": "float", "default": 0.0, "min": -180.0, "max": 180.0},
            "opacity": {"type": "float", "default": 1.0, "min": 0.0, "max": 1.0},
        },
    },
    "chroma_key": {
        "label": "Chroma Key",
        "category": "video",
        "params": {
            "key_color_type": {
                "type": "str",
                "default": "green",
                "values": ["green", "blue", "magenta", "custom"],
            },
            "similarity": {"type": "int", "default": 400, "min": 1, "max": 1000},
            "smoothness": {"type": "int", "default": 80, "min": 1, "max": 1000},
            "spill": {"type": "int", "default": 100, "min": 1, "max": 1000},
        },
    },
    "color_key": {
        "label": "Color Key",
        "category": "video",
        "params": {
            "key_color": {"type": "str", "default": "#00FF00"},
            "similarity": {"type": "int", "default": 400, "min": 1, "max": 1000},
            "smoothness": {"type": "int", "default": 80, "min": 1, "max": 1000},
        },
    },
    "lut": {
        "label": "Apply LUT",
        "category": "video",
        "params": {
            "path": {"type": "str", "default": ""},
            "amount": {"type": "float", "default": 1.0, "min": 0.0, "max": 1.0},
        },
    },
    "image_mask": {
        "label": "Image Mask/Blend",
        "category": "video",
        "params": {
            "path": {"type": "str", "default": ""},
            "type": {"type": "str", "default": "alpha", "values": ["alpha", "blend"]},
        },
    },
    "crop_pad": {
        "label": "Crop/Pad",
        "category": "video",
        "params": {
            "top": {"type": "int", "default": 0, "min": 0, "max": 8192},
            "bottom": {"type": "int", "default": 0, "min": 0, "max": 8192},
            "left": {"type": "int", "default": 0, "min": 0, "max": 8192},
            "right": {"type": "int", "default": 0, "min": 0, "max": 8192},
        },
    },
    "scroll": {
        "label": "Scroll",
        "category": "video",
        "params": {
            "speed_x": {"type": "float", "default": 0.0, "min": -5000.0, "max": 5000.0},
            "speed_y": {"type": "float", "default": 0.0, "min": -5000.0, "max": 5000.0},
            "loop": {"type": "bool", "default": True},
        },
    },
    "sharpen": {
        "label": "Sharpen",
        "category": "video",
        "params": {
            "sharpness": {"type": "float", "default": 0.08, "min": 0.0, "max": 1.0},
        },
    },
    "noise_suppress": {
        "label": "Noise Suppression",
        "category": "audio",
        "params": {
            "method": {
                "type": "str",
                "default": "rnnoise",
                "values": ["rnnoise", "speex", "nvafx"],
            },
            "suppress_level": {"type": "int", "default": -30, "min": -60, "max": 0},
        },
    },
    "gain": {
        "label": "Gain",
        "category": "audio",
        "params": {
            "db": {"type": "float", "default": 0.0, "min": -30.0, "max": 30.0},
        },
    },
    "compressor": {
        "label": "Compressor",
        "category": "audio",
        "params": {
            "ratio": {"type": "float", "default": 10.0, "min": 1.0, "max": 32.0},
            "threshold": {"type": "float", "default": -18.0, "min": -60.0, "max": 0.0},
            "attack": {"type": "int", "default": 6, "min": 1, "max": 500},
            "release": {"type": "int", "default": 60, "min": 1, "max": 1000},
            "output_gain": {"type": "float", "default": 0.0, "min": -30.0, "max": 30.0},
        },
    },
    "noise_gate": {
        "label": "Noise Gate",
        "category": "audio",
        "params": {
            "open_threshold": {
                "type": "float",
                "default": -26.0,
                "min": -96.0,
                "max": 0.0,
            },
            "close_threshold": {
                "type": "float",
                "default": -32.0,
                "min": -96.0,
                "max": 0.0,
            },
            "attack": {"type": "int", "default": 25, "min": 1, "max": 500},
            "hold": {"type": "int", "default": 200, "min": 1, "max": 1000},
            "release": {"type": "int", "default": 150, "min": 1, "max": 1000},
        },
    },
    "limiter": {
        "label": "Limiter",
        "category": "audio",
        "params": {
            "threshold": {"type": "float", "default": -6.0, "min": -60.0, "max": 0.0},
            "release": {"type": "int", "default": 60, "min": 1, "max": 1000},
        },
    },
}

__all__ = [
    "Any",
    "Dict",
    "FILTER_TYPES",
    "List",
    "Optional",
    "copy",
    "generate_id",
    "get_item",
    "unique_name",
    "validate_range",
]
