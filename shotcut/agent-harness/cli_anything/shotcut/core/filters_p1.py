# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART0 = {
    "brightness": {
        "service": "brightness",
        "category": "video",
        "description": "Adjust brightness and contrast",
        "params": {
            "level": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-2.0",
                "description": "Brightness level (1.0 = normal)",
            },
        },
    },
    "volume": {
        "service": "volume",
        "category": "audio",
        "description": "Adjust audio volume",
        "params": {
            "level": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-5.0",
                "description": "Volume level (1.0 = normal)",
            },
            "gain": {"type": "float", "default": "0.0", "description": "Gain in dB"},
        },
    },
    "blur": {
        "service": "frei0r.IIRblur",
        "category": "video",
        "description": "Gaussian blur effect",
        "params": {
            "amount": {
                "type": "float",
                "default": "0.2",
                "range": "0.0-1.0",
                "description": "Blur amount",
            },
        },
    },
    "crop": {
        "service": "crop",
        "category": "video",
        "description": "Crop the video frame",
        "params": {
            "left": {"type": "int", "default": "0", "description": "Pixels from left"},
            "right": {
                "type": "int",
                "default": "0",
                "description": "Pixels from right",
            },
            "top": {"type": "int", "default": "0", "description": "Pixels from top"},
            "bottom": {
                "type": "int",
                "default": "0",
                "description": "Pixels from bottom",
            },
        },
    },
    "mirror": {
        "service": "mirror",
        "category": "video",
        "description": "Mirror the video horizontally or vertically",
        "params": {
            "mirror": {
                "type": "string",
                "default": "horizontal",
                "description": "Mirror direction: horizontal, vertical, diagonal, xdiagonal, flip, flop",
            },
        },
    },
    "fadein-video": {
        "service": "brightness",
        "category": "video",
        "description": "Video fade in from black",
        "params": {
            "level": {
                "type": "string",
                "default": "00:00:00.000=0;00:00:01.000=1",
                "description": "Keyframed brightness (timecode=value pairs)",
            },
            "alpha": {"type": "float", "default": "1", "description": "Alpha value"},
        },
    },
    "fadeout-video": {
        "service": "brightness",
        "category": "video",
        "description": "Video fade out to black",
        "params": {
            "level": {
                "type": "string",
                "default": "00:00:00.000=1;00:00:01.000=0",
                "description": "Keyframed brightness (timecode=value pairs)",
            },
        },
    },
    "fadein-audio": {
        "service": "volume",
        "category": "audio",
        "description": "Audio fade in",
        "params": {
            "level": {
                "type": "string",
                "default": "00:00:00.000=0;00:00:01.000=1",
                "description": "Keyframed volume (timecode=value pairs)",
            },
        },
    },
}
