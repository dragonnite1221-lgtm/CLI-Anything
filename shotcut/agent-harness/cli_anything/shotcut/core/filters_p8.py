# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p1 import _FILTER_REGISTRY_PART0  # noqa: E402,E501
from .filters_p2 import _FILTER_REGISTRY_PART1  # noqa: E402,E501
from .filters_p3 import _FILTER_REGISTRY_PART2  # noqa: E402,E501
from .filters_p4 import _FILTER_REGISTRY_PART3  # noqa: E402,E501
from .filters_p5 import _FILTER_REGISTRY_PART4  # noqa: E402,E501
from .filters_p6 import _FILTER_REGISTRY_PART5  # noqa: E402,E501
from .filters_p7 import _FILTER_REGISTRY_PART6  # noqa: E402,E501
# fmt: on


_FILTER_REGISTRY_PART7 = {
    "lowpass": {
        "service": "ladspa.1052",
        "category": "audio",
        "description": "Low-pass audio filter",
        "params": {
            "0": {
                "type": "float",
                "default": "1000",
                "description": "Cutoff frequency (Hz)",
            },
            "1": {
                "type": "float",
                "default": "1",
                "description": "Stages (filter order)",
            },
        },
    },
    "highpass": {
        "service": "ladspa.1042",
        "category": "audio",
        "description": "High-pass audio filter",
        "params": {
            "0": {
                "type": "float",
                "default": "100",
                "description": "Cutoff frequency (Hz)",
            },
            "1": {
                "type": "float",
                "default": "1",
                "description": "Stages (filter order)",
            },
        },
    },
    "delay": {
        "service": "ladspa.1043",
        "category": "audio",
        "description": "Audio delay / echo effect",
        "params": {
            "0": {
                "type": "float",
                "default": "0.5",
                "description": "Delay time (seconds)",
            },
            "1": {"type": "float", "default": "0.3", "description": "Feedback"},
            "2": {"type": "float", "default": "0.5", "description": "Wet/dry mix"},
        },
    },
    "mute": {
        "service": "volume",
        "category": "audio",
        "description": "Mute audio (set volume to zero)",
        "params": {
            "gain": {
                "type": "float",
                "default": "-100",
                "description": "Gain in dB (-100 = silent)",
            },
        },
    },
    "balance": {
        "service": "panner",
        "category": "audio",
        "description": "Audio stereo balance / panning",
        "params": {
            "start": {
                "type": "float",
                "default": "0.5",
                "range": "0.0-1.0",
                "description": "Pan position (0=left, 0.5=center, 1=right)",
            },
        },
    },
}
FILTER_REGISTRY = {
    **_FILTER_REGISTRY_PART0,
    **_FILTER_REGISTRY_PART1,
    **_FILTER_REGISTRY_PART2,
    **_FILTER_REGISTRY_PART3,
    **_FILTER_REGISTRY_PART4,
    **_FILTER_REGISTRY_PART5,
    **_FILTER_REGISTRY_PART6,
    **_FILTER_REGISTRY_PART7,
}


def list_available_filters(category: Optional[str] = None) -> list[dict]:
    """List all available filters from the registry.

    Args:
        category: Filter by category ("video", "audio", or None for all)
    """
    result = []
    for name, info in sorted(FILTER_REGISTRY.items()):
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


def get_filter_info(filter_name: str) -> dict:
    """Get detailed info about a filter including its parameters."""
    if filter_name not in FILTER_REGISTRY:
        available = ", ".join(sorted(FILTER_REGISTRY.keys()))
        raise ValueError(f"Unknown filter: {filter_name!r}. Available: {available}")
    info = dict(FILTER_REGISTRY[filter_name])
    info["name"] = filter_name
    return info
