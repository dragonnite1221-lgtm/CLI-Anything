# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART1 = {
    "fadeout-audio": {
        "service": "volume",
        "category": "audio",
        "description": "Audio fade out",
        "params": {
            "level": {
                "type": "string",
                "default": "00:00:00.000=1;00:00:01.000=0",
                "description": "Keyframed volume (timecode=value pairs)",
            },
        },
    },
    "sepia": {
        "service": "sepia",
        "category": "video",
        "description": "Sepia tone effect",
        "params": {
            "u": {"type": "int", "default": "75", "description": "Chroma U value"},
            "v": {"type": "int", "default": "150", "description": "Chroma V value"},
        },
    },
    "charcoal": {
        "service": "charcoal",
        "category": "video",
        "description": "Charcoal drawing effect",
        "params": {
            "x_scatter": {
                "type": "int",
                "default": "1",
                "description": "Horizontal scatter",
            },
            "y_scatter": {
                "type": "int",
                "default": "1",
                "description": "Vertical scatter",
            },
        },
    },
    "saturation": {
        "service": "frei0r.saturat0r",
        "category": "video",
        "description": "Adjust color saturation",
        "params": {
            "saturation": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-3.0",
                "description": "Saturation (1.0 = normal, 0.0 = grayscale)",
            },
        },
    },
    "hue": {
        "service": "frei0r.hueshift0r",
        "category": "video",
        "description": "Shift hue of the image",
        "params": {
            "shift": {
                "type": "float",
                "default": "0.0",
                "range": "0.0-1.0",
                "description": "Hue shift amount (0.0-1.0 = full circle)",
            },
        },
    },
    "glow": {
        "service": "frei0r.glow",
        "category": "video",
        "description": "Glow/bloom effect",
        "params": {
            "blur": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Glow blur amount",
            },
        },
    },
    "text": {
        "service": "dynamictext",
        "category": "video",
        "description": "Text overlay on video",
        "params": {
            "argument": {
                "type": "string",
                "default": "Text Here",
                "description": "The text to display",
            },
            "geometry": {
                "type": "string",
                "default": "0%/0%:100%x100%:100",
                "description": "Position geometry (x/y:wxh:opacity)",
            },
            "family": {
                "type": "string",
                "default": "Sans",
                "description": "Font family",
            },
            "size": {"type": "int", "default": "48", "description": "Font size"},
            "fgcolour": {
                "type": "string",
                "default": "#ffffffff",
                "description": "Text color as #AARRGGBB",
            },
            "bgcolour": {
                "type": "string",
                "default": "#00000000",
                "description": "Background color as #AARRGGBB",
            },
            "valign": {
                "type": "string",
                "default": "middle",
                "description": "Vertical alignment: top, middle, bottom",
            },
            "halign": {
                "type": "string",
                "default": "center",
                "description": "Horizontal alignment: left, center, right",
            },
        },
    },
    "affine": {
        "service": "affine",
        "category": "video",
        "description": "Position, scale, and rotate",
        "params": {
            "transition.geometry": {
                "type": "string",
                "default": "0/0:100%x100%:100",
                "description": "Geometry: x/y:wxh:opacity",
            },
            "transition.fix_rotate_x": {
                "type": "float",
                "default": "0",
                "description": "Rotation around X axis (degrees)",
            },
            "transition.fix_rotate_y": {
                "type": "float",
                "default": "0",
                "description": "Rotation around Y axis (degrees)",
            },
            "transition.fix_rotate_z": {
                "type": "float",
                "default": "0",
                "description": "Rotation around Z axis (degrees)",
            },
        },
    },
}
