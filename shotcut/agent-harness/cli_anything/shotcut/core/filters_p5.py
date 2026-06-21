# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART4 = {
    "sharpen": {
        "service": "frei0r.sharpness",
        "category": "video",
        "description": "Sharpen the image",
        "params": {
            "amount": {
                "type": "float",
                "default": "0.3",
                "range": "0.0-1.0",
                "description": "Sharpness amount",
            },
            "size": {
                "type": "float",
                "default": "0.0",
                "range": "0.0-1.0",
                "description": "Sharpening kernel size",
            },
        },
    },
    "vignette": {
        "service": "frei0r.vignette",
        "category": "video",
        "description": "Vignette (darken edges)",
        "params": {
            "aspect": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Aspect ratio of vignette",
            },
            "clearcenter": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Size of clear center area",
            },
            "soft": {
                "type": "float",
                "default": "0.6",
                "range": "0.0-1.0",
                "description": "Softness of vignette edge",
            },
        },
    },
    "grain": {
        "service": "frei0r.rgbnoise",
        "category": "video",
        "description": "Add film grain / noise",
        "params": {
            "noise": {
                "type": "float",
                "default": "0.2",
                "range": "0.0-1.0",
                "description": "Noise amount",
            },
        },
    },
    "lens-correction": {
        "service": "frei0r.lenscorrection",
        "category": "video",
        "description": "Lens distortion correction (barrel/pincushion)",
        "params": {
            "xcenter": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Center X position",
            },
            "ycenter": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Center Y position",
            },
            "correctionnearcenter": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Correction near center",
            },
            "correctionnearedges": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Correction near edges",
            },
        },
    },
    "pixelize": {
        "service": "frei0r.pixeliz0r",
        "category": "video",
        "description": "Pixelation / mosaic effect",
        "params": {
            "blocksizex": {
                "type": "float",
                "default": "0.05",
                "range": "0.0-1.0",
                "description": "Block size X (fraction of width)",
            },
            "blocksizey": {
                "type": "float",
                "default": "0.05",
                "range": "0.0-1.0",
                "description": "Block size Y (fraction of height)",
            },
        },
    },
    "wave": {
        "service": "wave",
        "category": "video",
        "description": "Wave distortion effect",
        "params": {
            "start": {"type": "int", "default": "0", "description": "Start frame"},
            "speed": {"type": "float", "default": "5.0", "description": "Wave speed"},
            "deformX": {
                "type": "int",
                "default": "1",
                "description": "Deform in X (0 or 1)",
            },
            "deformY": {
                "type": "int",
                "default": "1",
                "description": "Deform in Y (0 or 1)",
            },
            "amplitude": {
                "type": "int",
                "default": "25",
                "description": "Wave amplitude in pixels",
            },
        },
    },
    "oldfilm": {
        "service": "oldfilm",
        "category": "video",
        "description": "Old film effect (scratches, dust, flickering)",
        "params": {
            "brightnessdelta_up": {
                "type": "int",
                "default": "20",
                "description": "Brightness variation up",
            },
            "brightnessdelta_down": {
                "type": "int",
                "default": "30",
                "description": "Brightness variation down",
            },
            "unevendevelop_duration": {
                "type": "int",
                "default": "70",
                "description": "Uneven development duration",
            },
        },
    },
    "vertigo": {
        "service": "frei0r.vertigo",
        "category": "video",
        "description": "Vertigo / dolly-zoom distortion effect",
        "params": {
            "phaseincrement": {
                "type": "float",
                "default": "0.02",
                "range": "0.0-1.0",
                "description": "Phase increment",
            },
            "zoomrate": {
                "type": "float",
                "default": "0.2",
                "range": "0.0-1.0",
                "description": "Zoom rate",
            },
        },
    },
}
