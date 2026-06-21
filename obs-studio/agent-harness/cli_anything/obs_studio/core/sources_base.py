# ruff: noqa: E501
"""OBS Studio CLI - Source management."""

import copy
from typing import Dict, Any, List, Optional
from cli_anything.obs_studio.utils.obs_utils import (
    generate_id,
    unique_name,
    get_item,
    validate_range,
)


SOURCE_TYPES = {
    "video_capture": {
        "label": "Video Capture Device",
        "category": "video",
        "default_settings": {"device": "", "resolution": "1920x1080", "fps": 30},
    },
    "display_capture": {
        "label": "Display Capture",
        "category": "video",
        "default_settings": {"display": 0, "capture_cursor": True},
    },
    "window_capture": {
        "label": "Window Capture",
        "category": "video",
        "default_settings": {"window": "", "capture_cursor": True},
    },
    "image": {
        "label": "Image",
        "category": "media",
        "default_settings": {"file": "", "unload_when_hidden": True},
    },
    "media": {
        "label": "Media Source",
        "category": "media",
        "default_settings": {
            "local_file": "",
            "looping": False,
            "restart_on_activate": True,
        },
    },
    "browser": {
        "label": "Browser Source",
        "category": "web",
        "default_settings": {"url": "", "width": 800, "height": 600, "css": ""},
    },
    "text": {
        "label": "Text (FreeType 2)",
        "category": "text",
        "default_settings": {
            "text": "",
            "font": "Sans Serif",
            "size": 36,
            "color": "#FFFFFF",
        },
    },
    "color": {
        "label": "Color Source",
        "category": "utility",
        "default_settings": {"color": "#000000", "width": 1920, "height": 1080},
    },
    "audio_input": {
        "label": "Audio Input Capture",
        "category": "audio",
        "default_settings": {"device": ""},
    },
    "audio_output": {
        "label": "Audio Output Capture",
        "category": "audio",
        "default_settings": {"device": ""},
    },
    "group": {
        "label": "Group",
        "category": "utility",
        "default_settings": {"items": []},
    },
    "scene": {
        "label": "Scene",
        "category": "utility",
        "default_settings": {"scene_name": ""},
    },
}

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "SOURCE_TYPES",
    "copy",
    "generate_id",
    "get_item",
    "unique_name",
    "validate_range",
]
