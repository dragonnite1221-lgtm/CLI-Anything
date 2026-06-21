# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART2 = {
    "speed": {
        "service": "timewarp",
        "category": "video",
        "description": "Change playback speed",
        "params": {
            "speed": {
                "type": "float",
                "default": "1.0",
                "description": "Playback speed (2.0 = double speed, 0.5 = half speed)",
            },
        },
    },
    "chroma-key": {
        "service": "frei0r.select0r",
        "category": "video",
        "description": "Chroma key (green/blue screen removal)",
        "params": {
            "color_to_select": {
                "type": "string",
                "default": "0.0 0.8 0.0",
                "description": "Color to key out (R G B, 0.0-1.0)",
            },
            "delta_r__g___b_": {
                "type": "float",
                "default": "0.2",
                "range": "0.0-1.0",
                "description": "Color tolerance",
            },
            "selection_subspace": {
                "type": "float",
                "default": "0.5",
                "description": "Subspace (0=HCI, 0.5=HSI)",
            },
        },
    },
    "chroma-key-advanced": {
        "service": "frei0r.keyspillm0pup",
        "category": "video",
        "description": "Advanced chroma key with spill suppression",
        "params": {
            "key_color": {
                "type": "string",
                "default": "0.0 0.8 0.0",
                "description": "Key color (R G B, 0.0-1.0)",
            },
            "target_color": {
                "type": "string",
                "default": "0.5 0.5 0.5",
                "description": "Target replacement color",
            },
            "mask_type": {
                "type": "int",
                "default": "0",
                "description": "Mask type (0-3)",
            },
            "tolerance": {
                "type": "float",
                "default": "0.24",
                "range": "0.0-1.0",
                "description": "Color tolerance",
            },
        },
    },
    "bluescreen": {
        "service": "frei0r.bluescreen0r",
        "category": "video",
        "description": "Blue/green screen removal (simpler than chroma-key)",
        "params": {
            "color": {
                "type": "string",
                "default": "0.0 0.85 0.0",
                "description": "Screen color (R G B, 0.0-1.0)",
            },
            "distance": {
                "type": "float",
                "default": "0.288",
                "range": "0.0-1.0",
                "description": "Color distance threshold",
            },
        },
    },
    "color-grading": {
        "service": "frei0r.coloradj_RGB",
        "category": "video",
        "description": "RGB color adjustment (lift/gain per channel)",
        "params": {
            "r": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Red adjustment (0.5 = neutral)",
            },
            "g": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Green adjustment",
            },
            "b": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Blue adjustment",
            },
            "action": {
                "type": "int",
                "default": "0",
                "description": "0=Shadows, 1=Midtones, 2=Highlights",
            },
            "keep_luma": {
                "type": "int",
                "default": "0",
                "description": "Preserve luminance (0 or 1)",
            },
        },
    },
    "levels": {
        "service": "frei0r.levels",
        "category": "video",
        "description": "Levels adjustment (input/output black/white points)",
        "params": {
            "input_black_level": {
                "type": "float",
                "default": "0.0",
                "range": "0.0-1.0",
                "description": "Input black level",
            },
            "input_white_level": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-1.0",
                "description": "Input white level",
            },
            "gamma": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Gamma (0.5 = 1.0 gamma)",
            },
            "channel": {
                "type": "int",
                "default": "0",
                "description": "Channel: 0=All, 1=R, 2=G, 3=B",
            },
        },
    },
    "white-balance": {
        "service": "frei0r.balanc0r",
        "category": "video",
        "description": "White balance / color temperature adjustment",
        "params": {
            "neutral_color": {
                "type": "string",
                "default": "0.5 0.5 0.5",
                "description": "Neutral color reference (R G B)",
            },
        },
    },
    "contrast": {
        "service": "frei0r.contrast0r",
        "category": "video",
        "description": "Adjust contrast",
        "params": {
            "contrast": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Contrast level (0.5 = normal)",
            },
        },
    },
}
