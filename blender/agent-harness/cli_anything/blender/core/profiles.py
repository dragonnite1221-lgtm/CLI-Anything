"""Blender scene render profiles (split from scene.py)."""

from typing import Any, Dict, List


# Scene profiles (common setups)
PROFILES = {
    "default": {
        "resolution_x": 1920, "resolution_y": 1080,
        "engine": "CYCLES", "samples": 128, "fps": 24,
    },
    "preview": {
        "resolution_x": 960, "resolution_y": 540,
        "engine": "EEVEE", "samples": 16, "fps": 24,
    },
    "hd720p": {
        "resolution_x": 1280, "resolution_y": 720,
        "engine": "CYCLES", "samples": 64, "fps": 24,
    },
    "hd1080p": {
        "resolution_x": 1920, "resolution_y": 1080,
        "engine": "CYCLES", "samples": 128, "fps": 24,
    },
    "4k": {
        "resolution_x": 3840, "resolution_y": 2160,
        "engine": "CYCLES", "samples": 256, "fps": 24,
    },
    "instagram_square": {
        "resolution_x": 1080, "resolution_y": 1080,
        "engine": "EEVEE", "samples": 64, "fps": 30,
    },
    "youtube_short": {
        "resolution_x": 1080, "resolution_y": 1920,
        "engine": "EEVEE", "samples": 64, "fps": 30,
    },
    "product_render": {
        "resolution_x": 2048, "resolution_y": 2048,
        "engine": "CYCLES", "samples": 512, "fps": 24,
    },
    "animation_preview": {
        "resolution_x": 1280, "resolution_y": 720,
        "engine": "EEVEE", "samples": 16, "fps": 24,
    },
    "print_a4_300dpi": {
        "resolution_x": 2480, "resolution_y": 3508,
        "engine": "CYCLES", "samples": 256, "fps": 24,
    },
}

PROJECT_VERSION = "1.0"


def list_profiles() -> List[Dict[str, Any]]:
    """List all available scene profiles."""
    result = []
    for name, p in PROFILES.items():
        result.append({
            "name": name,
            "resolution": f"{p['resolution_x']}x{p['resolution_y']}",
            "engine": p["engine"],
            "samples": p["samples"],
            "fps": p["fps"],
        })
    return result
