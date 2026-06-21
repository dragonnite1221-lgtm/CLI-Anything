# ruff: noqa: E501
"""Kdenlive CLI - Filter (effect) management module."""

from typing import Dict, Any, List, Optional


FILTER_REGISTRY = {
    "brightness": {
        "mlt_service": "brightness",
        "category": "color",
        "params": {
            "level": {"type": "float", "default": 1.0, "min": 0.0, "max": 5.0},
        },
    },
    "contrast": {
        "mlt_service": "brightness",
        "category": "color",
        "params": {
            "level": {"type": "float", "default": 1.0, "min": 0.0, "max": 5.0},
        },
    },
    "saturation": {
        "mlt_service": "avfilter.eq",
        "category": "color",
        "params": {
            "saturation": {"type": "float", "default": 1.0, "min": 0.0, "max": 3.0},
        },
    },
    "blur": {
        "mlt_service": "boxblur",
        "category": "effect",
        "params": {
            "hblur": {"type": "int", "default": 2, "min": 0, "max": 100},
            "vblur": {"type": "int", "default": 2, "min": 0, "max": 100},
        },
    },
    "fade_in_video": {
        "mlt_service": "brightness",
        "kdenlive_name": "fade_from_black",
        "category": "transition",
        "params": {
            "duration": {"type": "float", "default": 1.0, "min": 0.01, "max": 60.0},
        },
    },
    "fade_out_video": {
        "mlt_service": "brightness",
        "kdenlive_name": "fade_to_black",
        "category": "transition",
        "params": {
            "duration": {"type": "float", "default": 1.0, "min": 0.01, "max": 60.0},
        },
    },
    "fade_in_audio": {
        "mlt_service": "volume",
        "kdenlive_name": "fadein",
        "category": "transition",
        "params": {
            "duration": {"type": "float", "default": 1.0, "min": 0.01, "max": 60.0},
        },
    },
    "fade_out_audio": {
        "mlt_service": "volume",
        "kdenlive_name": "fadeout",
        "category": "transition",
        "params": {
            "duration": {"type": "float", "default": 1.0, "min": 0.01, "max": 60.0},
        },
    },
    "volume": {
        "mlt_service": "volume",
        "category": "audio",
        "params": {
            "gain": {"type": "float", "default": 1.0, "min": 0.0, "max": 10.0},
        },
    },
    "crop": {
        "mlt_service": "crop",
        "category": "effect",
        "params": {
            "left": {"type": "int", "default": 0, "min": 0, "max": 9999},
            "right": {"type": "int", "default": 0, "min": 0, "max": 9999},
            "top": {"type": "int", "default": 0, "min": 0, "max": 9999},
            "bottom": {"type": "int", "default": 0, "min": 0, "max": 9999},
        },
    },
    "rotate": {
        "mlt_service": "affine",
        "category": "effect",
        "params": {
            "angle": {"type": "float", "default": 0.0, "min": -360.0, "max": 360.0},
        },
    },
    "speed": {
        "mlt_service": "timewarp",
        "kdenlive_name": "speed",
        "category": "effect",
        "params": {
            "speed": {"type": "float", "default": 1.0, "min": 0.01, "max": 100.0},
        },
    },
    "chroma_key": {
        "mlt_service": "frei0r.select0r",
        "category": "keying",
        "params": {
            "color": {"type": "str", "default": "#00ff00"},
            "variance": {"type": "float", "default": 0.15, "min": 0.0, "max": 1.0},
        },
    },
}

__all__ = ["Any", "Dict", "FILTER_REGISTRY", "List", "Optional"]
