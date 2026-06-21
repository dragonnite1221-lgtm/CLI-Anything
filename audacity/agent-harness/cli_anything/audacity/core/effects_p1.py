# ruff: noqa: F403, F405, E501
from .effects_base import *  # noqa: F403


_EFFECT_REGISTRY_PART0 = {
    "amplify": {
        "category": "volume",
        "description": "Amplify or attenuate audio by a dB amount",
        "params": {
            "gain_db": {
                "type": "float",
                "default": 0.0,
                "min": -60,
                "max": 60,
                "description": "Gain in decibels",
            },
        },
    },
    "normalize": {
        "category": "volume",
        "description": "Normalize audio to a target peak level",
        "params": {
            "target_db": {
                "type": "float",
                "default": -1.0,
                "min": -60,
                "max": 0,
                "description": "Target peak level in dB",
            },
        },
    },
    "fade_in": {
        "category": "fade",
        "description": "Apply a fade-in at the start",
        "params": {
            "duration": {
                "type": "float",
                "default": 1.0,
                "min": 0.01,
                "max": 300,
                "description": "Fade duration in seconds",
            },
        },
    },
    "fade_out": {
        "category": "fade",
        "description": "Apply a fade-out at the end",
        "params": {
            "duration": {
                "type": "float",
                "default": 1.0,
                "min": 0.01,
                "max": 300,
                "description": "Fade duration in seconds",
            },
        },
    },
    "reverse": {
        "category": "transform",
        "description": "Reverse the audio",
        "params": {},
    },
    "silence": {
        "category": "generate",
        "description": "Generate silence",
        "params": {
            "duration": {
                "type": "float",
                "default": 1.0,
                "min": 0.01,
                "max": 3600,
                "description": "Silence duration in seconds",
            },
        },
    },
    "tone": {
        "category": "generate",
        "description": "Generate a sine wave tone",
        "params": {
            "frequency": {
                "type": "float",
                "default": 440.0,
                "min": 20,
                "max": 20000,
                "description": "Frequency in Hz",
            },
            "duration": {
                "type": "float",
                "default": 1.0,
                "min": 0.01,
                "max": 3600,
                "description": "Duration in seconds",
            },
            "amplitude": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0,
                "description": "Amplitude (0.0-1.0)",
            },
        },
    },
    "change_speed": {
        "category": "transform",
        "description": "Change playback speed (also changes pitch)",
        "params": {
            "factor": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 10.0,
                "description": "Speed factor (2.0 = double speed)",
            },
        },
    },
}
