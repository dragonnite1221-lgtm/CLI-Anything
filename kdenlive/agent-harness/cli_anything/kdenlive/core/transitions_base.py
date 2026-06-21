# ruff: noqa: E501
"""Kdenlive CLI - Transition management module."""

from typing import Dict, Any, List, Optional


TRANSITION_TYPES = {
    "dissolve": {
        "mlt_service": "luma",
        "params": {
            "duration": {"type": "float", "default": 1.0, "min": 0.01, "max": 60.0},
            "softness": {"type": "float", "default": 0.0, "min": 0.0, "max": 1.0},
        },
    },
    "wipe": {
        "mlt_service": "luma",
        "params": {
            "duration": {"type": "float", "default": 1.0, "min": 0.01, "max": 60.0},
            "resource": {"type": "str", "default": ""},
            "softness": {"type": "float", "default": 0.0, "min": 0.0, "max": 1.0},
        },
    },
    "slide": {
        "mlt_service": "affine",
        "params": {
            "duration": {"type": "float", "default": 1.0, "min": 0.01, "max": 60.0},
            "direction": {"type": "str", "default": "left"},
        },
    },
    "composite": {
        "mlt_service": "composite",
        "params": {
            "fill": {"type": "int", "default": 1, "min": 0, "max": 1},
            "aligned": {"type": "int", "default": 1, "min": 0, "max": 1},
        },
    },
    "affine": {
        "mlt_service": "affine",
        "params": {
            "distort": {"type": "int", "default": 0, "min": 0, "max": 1},
        },
    },
}

__all__ = ["Any", "Dict", "List", "Optional", "TRANSITION_TYPES"]
