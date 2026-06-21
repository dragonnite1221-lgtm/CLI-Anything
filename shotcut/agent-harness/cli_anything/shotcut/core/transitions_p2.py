# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403

# fmt: off
from .transitions_p1 import _TRANSITION_REGISTRY_PART0  # noqa: E402,E501
# fmt: on


_TRANSITION_REGISTRY_PART1 = {
    "bar-vertical": {
        "service": "luma",
        "category": "video",
        "description": "Vertical bars wipe",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma06.pgm",
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
    "diagonal": {
        "service": "luma",
        "category": "video",
        "description": "Diagonal wipe",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma07.pgm",
                "description": "Luma pattern file (diagonal)",
            },
            "softness": {
                "type": "float",
                "default": "0.1",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
        },
    },
    "clock": {
        "service": "luma",
        "category": "video",
        "description": "Clock wipe (radial sweep)",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma16.pgm",
                "description": "Luma pattern file (clock)",
            },
            "softness": {
                "type": "float",
                "default": "0.1",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
        },
    },
    "iris-circle": {
        "service": "luma",
        "category": "video",
        "description": "Circular iris wipe",
        "params": {
            "resource": {
                "type": "string",
                "default": "%luma22.pgm",
                "description": "Luma pattern file (iris)",
            },
            "softness": {
                "type": "float",
                "default": "0.2",
                "range": "0.0-1.0",
                "description": "Edge softness",
            },
        },
    },
    "crossfade": {
        "service": "mix",
        "category": "audio",
        "description": "Audio crossfade between clips",
        "params": {
            "start": {
                "type": "float",
                "default": "0.0",
                "range": "0.0-1.0",
                "description": "Start mix level",
            },
            "end": {
                "type": "float",
                "default": "1.0",
                "range": "0.0-1.0",
                "description": "End mix level",
            },
        },
    },
}
TRANSITION_REGISTRY = {**_TRANSITION_REGISTRY_PART0, **_TRANSITION_REGISTRY_PART1}


def list_available_transitions(category: Optional[str] = None) -> list[dict]:
    """List all available transition types."""
    result = []
    for name, info in sorted(TRANSITION_REGISTRY.items()):
        if category and info["category"] != category:
            continue
        result.append(
            {
                "name": name,
                "service": info["service"],
                "category": info["category"],
                "description": info["description"],
                "params": list(info["params"].keys()),
            }
        )
    return result


def get_transition_info(transition_name: str) -> dict:
    """Get detailed info about a transition type."""
    if transition_name not in TRANSITION_REGISTRY:
        available = ", ".join(sorted(TRANSITION_REGISTRY.keys()))
        raise ValueError(
            f"Unknown transition: {transition_name!r}. Available: {available}"
        )
    info = dict(TRANSITION_REGISTRY[transition_name])
    info["name"] = transition_name
    return info
