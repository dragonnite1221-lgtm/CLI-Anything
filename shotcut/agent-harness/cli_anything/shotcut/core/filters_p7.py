# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART6 = {
    "flip-vertical": {
        "service": "avfilter.vflip",
        "category": "video",
        "description": "Flip video vertically",
        "params": {},
    },
    "opacity": {
        "service": "brightness",
        "category": "video",
        "description": "Adjust clip opacity / transparency",
        "params": {
            "alpha": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-1.0",
                "description": "Opacity (0.0=transparent, 1.0=opaque)",
            },
            "level": {
                "type": "float",
                "default": "1.0",
                "description": "Brightness level",
            },
        },
    },
    "mask-shape": {
        "service": "frei0r.alphaspot",
        "category": "video",
        "description": "Shape mask (rectangle, ellipse, triangle)",
        "params": {
            "position_x": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Center X position",
            },
            "position_y": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Center Y position",
            },
            "size_x": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Width",
            },
            "size_y": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Height",
            },
            "shape": {
                "type": "int",
                "default": "0",
                "description": "Shape: 0=Rectangle, 1=Ellipse, 2=Triangle, 3=Diamond",
            },
            "operation": {
                "type": "int",
                "default": "0",
                "description": "Operation: 0=Write on clear, 1=Max, 2=Min, 3=Add, 4=Subtract",
            },
        },
    },
    "mask-from-file": {
        "service": "frei0r.alphagrad",
        "category": "video",
        "description": "Gradient alpha mask",
        "params": {
            "position": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Position of gradient",
            },
            "tilt": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Tilt angle of gradient",
            },
            "min": {
                "type": "float",
                "default": "0.0",
                "range": "0.0-1.0",
                "description": "Minimum alpha value",
            },
            "max": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-1.0",
                "description": "Maximum alpha value",
            },
        },
    },
    "equalizer": {
        "service": "ladspa.1901",
        "category": "audio",
        "description": "3-band audio equalizer",
        "params": {
            "0": {
                "type": "float",
                "default": "0",
                "range": "-70-30",
                "description": "Low band gain (dB)",
            },
            "1": {
                "type": "float",
                "default": "0",
                "range": "-70-30",
                "description": "Mid band gain (dB)",
            },
            "2": {
                "type": "float",
                "default": "0",
                "range": "-70-30",
                "description": "High band gain (dB)",
            },
        },
    },
    "compressor": {
        "service": "ladspa.1913",
        "category": "audio",
        "description": "Dynamic range compressor",
        "params": {
            "0": {"type": "float", "default": "0", "description": "Attack (ms)"},
            "1": {"type": "float", "default": "0.5", "description": "Release (ms)"},
            "2": {"type": "float", "default": "0", "description": "Threshold (dB)"},
            "3": {"type": "float", "default": "1", "description": "Ratio"},
            "4": {"type": "float", "default": "0", "description": "Knee radius (dB)"},
            "5": {"type": "float", "default": "0", "description": "Makeup gain (dB)"},
        },
    },
    "reverb": {
        "service": "ladspa.1216",
        "category": "audio",
        "description": "Reverb effect (room simulation)",
        "params": {
            "0": {"type": "float", "default": "0.75", "description": "Room size"},
            "1": {"type": "float", "default": "0.5", "description": "Damping"},
            "2": {"type": "float", "default": "0.5", "description": "Wet level"},
            "3": {"type": "float", "default": "1.0", "description": "Dry level"},
            "4": {"type": "float", "default": "0.5", "description": "Width"},
        },
    },
    "normalize-audio": {
        "service": "loudness",
        "category": "audio",
        "description": "Normalize audio loudness (EBU R128)",
        "params": {
            "target_loudness": {
                "type": "float",
                "default": "-23.0",
                "description": "Target loudness in LUFS",
            },
        },
    },
}
