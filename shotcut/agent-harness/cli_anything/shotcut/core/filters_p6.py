# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


_FILTER_REGISTRY_PART5 = {
    "elastic-scale": {
        "service": "frei0r.elastic_scale",
        "category": "video",
        "description": "Elastic scaling (non-linear stretch for aspect ratio fix)",
        "params": {
            "center": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Center of linear region",
            },
            "linearwidth": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Width of linear region",
            },
            "nonlinearscalefactor": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Non-linear stretch factor",
            },
        },
    },
    "denoise": {
        "service": "frei0r.hqdn3d",
        "category": "video",
        "description": "High-quality 3D denoiser",
        "params": {
            "spatial": {
                "type": "float",
                "default": "0.04",
                "range": "0.0-1.0",
                "description": "Spatial denoise strength",
            },
            "temporal": {
                "type": "float",
                "default": "0.06",
                "range": "0.0-1.0",
                "description": "Temporal denoise strength",
            },
        },
    },
    "stabilize": {
        "service": "vidstab",
        "category": "video",
        "description": "Video stabilization (reduce camera shake)",
        "params": {
            "shakiness": {
                "type": "int",
                "default": "5",
                "range": "1-10",
                "description": "Shakiness detection (1=little, 10=very shaky)",
            },
            "accuracy": {
                "type": "int",
                "default": "15",
                "range": "1-15",
                "description": "Detection accuracy",
            },
            "smoothing": {
                "type": "int",
                "default": "10",
                "description": "Smoothing strength (frames)",
            },
            "zoom": {
                "type": "int",
                "default": "0",
                "description": "Additional zoom (%)",
            },
        },
    },
    "rich-text": {
        "service": "qtext",
        "category": "video",
        "description": "Rich text overlay with HTML support",
        "params": {
            "argument": {
                "type": "string",
                "default": "<h1>Title</h1>",
                "description": "HTML text content",
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
            "fgcolour": {
                "type": "string",
                "default": "#ffffffff",
                "description": "Foreground color (#AARRGGBB)",
            },
            "bgcolour": {
                "type": "string",
                "default": "#00000000",
                "description": "Background color (#AARRGGBB)",
            },
        },
    },
    "timer": {
        "service": "timer",
        "category": "video",
        "description": "Timer/countdown overlay",
        "params": {
            "format": {
                "type": "string",
                "default": "%M:%S",
                "description": "Time format string",
            },
            "duration": {
                "type": "string",
                "default": "00:00:10.000",
                "description": "Timer duration",
            },
            "direction": {
                "type": "string",
                "default": "down",
                "description": "Count direction: up or down",
            },
            "geometry": {
                "type": "string",
                "default": "0%/0%:100%x100%:100",
                "description": "Position geometry",
            },
        },
    },
    "size-position": {
        "service": "affine",
        "category": "video",
        "description": "Size, position, and rotation (picture-in-picture ready)",
        "params": {
            "transition.geometry": {
                "type": "string",
                "default": "0/0:100%x100%:100",
                "description": "Geometry: x/y:wxh:opacity",
            },
            "transition.fix_rotate_x": {
                "type": "float",
                "default": "0",
                "description": "X rotation (degrees)",
            },
            "transition.fix_rotate_y": {
                "type": "float",
                "default": "0",
                "description": "Y rotation (degrees)",
            },
            "transition.fix_rotate_z": {
                "type": "float",
                "default": "0",
                "description": "Z rotation (degrees)",
            },
            "background": {
                "type": "string",
                "default": "color:#00000000",
                "description": "Background (color:#AARRGGBB or path)",
            },
        },
    },
    "rotate-scale": {
        "service": "affine",
        "category": "video",
        "description": "Rotate and scale (centered rotation)",
        "params": {
            "transition.fix_rotate_z": {
                "type": "float",
                "default": "0",
                "description": "Rotation angle (degrees)",
            },
            "transition.scale_x": {
                "type": "float",
                "default": "1.0",
                "description": "Scale X (1.0 = 100%)",
            },
            "transition.scale_y": {
                "type": "float",
                "default": "1.0",
                "description": "Scale Y (1.0 = 100%)",
            },
        },
    },
    "flip-horizontal": {
        "service": "avfilter.hflip",
        "category": "video",
        "description": "Flip video horizontally",
        "params": {},
    },
}
