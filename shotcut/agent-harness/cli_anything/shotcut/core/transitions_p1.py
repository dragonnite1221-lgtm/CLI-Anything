# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403


_TRANSITION_REGISTRY_PART0 = {
    "dissolve": {
        "service": "luma",
        "category": "video",
        "description": "Cross-dissolve between two clips",
        "params": {
            "softness": {
                "type": "float",
                "default": "0",
                "range": "0.0-1.0",
                "description": "Edge softness of the transition",
            },
            "invert": {
                "type": "int",
                "default": "0",
                "description": "Invert the transition (0 or 1)",
            },
        },
    },
    "wipe-left": {
        "service": "luma",
        "category": "video",
        "description": "Wipe from right to left",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma01.pgm",
                "description": "Luma pattern file",
            },
            "softness": {
                "type": "float",
                "default": "0.1",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
        },
    },
    "wipe-right": {
        "service": "luma",
        "category": "video",
        "description": "Wipe from left to right",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma01.pgm",
                "description": "Luma pattern file",
            },
            "softness": {
                "type": "float",
                "default": "0.1",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
            "invert": {
                "type": "int",
                "default": "1",
                "description": "Invert direction",
            },
        },
    },
    "wipe-down": {
        "service": "luma",
        "category": "video",
        "description": "Wipe from top to bottom",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma04.pgm",
                "description": "Luma pattern file (vertical)",
            },
            "softness": {
                "type": "float",
                "default": "0.1",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
        },
    },
    "wipe-up": {
        "service": "luma",
        "category": "video",
        "description": "Wipe from bottom to top",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma04.pgm",
                "description": "Luma pattern file (vertical)",
            },
            "softness": {
                "type": "float",
                "default": "0.1",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
            "invert": {
                "type": "int",
                "default": "1",
                "description": "Invert direction",
            },
        },
    },
    "bar-horizontal": {
        "service": "luma",
        "category": "video",
        "description": "Horizontal bars wipe",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma05.pgm",
                "description": "Luma pattern file",
            },
            "softness": {
                "type": "float",
                "default": "0.1",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
        },
    },
}
