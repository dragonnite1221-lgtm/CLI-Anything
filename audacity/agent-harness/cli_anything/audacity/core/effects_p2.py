# ruff: noqa: F403, F405, E501
from .effects_base import *  # noqa: F403

# fmt: off
from .effects_p1 import _EFFECT_REGISTRY_PART0  # noqa: E402,E501
# fmt: on


_EFFECT_REGISTRY_PART1 = {
    "change_pitch": {
        "category": "transform",
        "description": "Change pitch by semitones",
        "params": {
            "semitones": {
                "type": "float",
                "default": 0.0,
                "min": -24,
                "max": 24,
                "description": "Pitch shift in semitones",
            },
        },
    },
    "echo": {
        "category": "delay",
        "description": "Add echo/delay effect",
        "params": {
            "delay_ms": {
                "type": "float",
                "default": 500.0,
                "min": 1,
                "max": 5000,
                "description": "Delay time in milliseconds",
            },
            "decay": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0,
                "description": "Echo decay factor",
            },
        },
    },
    "low_pass": {
        "category": "eq",
        "description": "Low-pass filter (cut high frequencies)",
        "params": {
            "cutoff": {
                "type": "float",
                "default": 1000.0,
                "min": 20,
                "max": 20000,
                "description": "Cutoff frequency in Hz",
            },
        },
    },
    "high_pass": {
        "category": "eq",
        "description": "High-pass filter (cut low frequencies)",
        "params": {
            "cutoff": {
                "type": "float",
                "default": 100.0,
                "min": 20,
                "max": 20000,
                "description": "Cutoff frequency in Hz",
            },
        },
    },
    "compress": {
        "category": "dynamics",
        "description": "Dynamic range compression",
        "params": {
            "threshold": {
                "type": "float",
                "default": -20.0,
                "min": -60,
                "max": 0,
                "description": "Threshold in dB",
            },
            "ratio": {
                "type": "float",
                "default": 4.0,
                "min": 1.0,
                "max": 20.0,
                "description": "Compression ratio",
            },
            "attack": {
                "type": "float",
                "default": 5.0,
                "min": 0.1,
                "max": 1000,
                "description": "Attack time in ms",
            },
            "release": {
                "type": "float",
                "default": 50.0,
                "min": 1,
                "max": 5000,
                "description": "Release time in ms",
            },
        },
    },
    "limit": {
        "category": "dynamics",
        "description": "Hard limiter",
        "params": {
            "threshold_db": {
                "type": "float",
                "default": -1.0,
                "min": -60,
                "max": 0,
                "description": "Limiter threshold in dB",
            },
        },
    },
    "change_tempo": {
        "category": "transform",
        "description": "Change tempo without changing pitch",
        "params": {
            "factor": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 10.0,
                "description": "Tempo factor (2.0 = double tempo)",
            },
        },
    },
    "noise_reduction": {
        "category": "restoration",
        "description": "Reduce background noise",
        "params": {
            "reduction_db": {
                "type": "float",
                "default": 12.0,
                "min": 0,
                "max": 48,
                "description": "Noise reduction amount in dB",
            },
        },
    },
}
EFFECT_REGISTRY = {**_EFFECT_REGISTRY_PART0, **_EFFECT_REGISTRY_PART1}


def list_available(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available effects, optionally filtered by category."""
    result = []
    for name, info in EFFECT_REGISTRY.items():
        if category and info["category"] != category:
            continue
        result.append(
            {
                "name": name,
                "category": info["category"],
                "description": info["description"],
                "param_count": len(info["params"]),
            }
        )
    return result
