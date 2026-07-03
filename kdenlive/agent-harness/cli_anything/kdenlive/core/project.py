"""Kdenlive CLI - Project management module."""

import json
import os
import copy
from datetime import datetime
from typing import Optional, Dict, Any, List

# Re-exported for backward compatibility (moved to profiles.py).
from .profiles import PROFILES, PROJECT_VERSION, list_profiles  # noqa: F401


def create_project(
    name: str = "untitled",
    profile: Optional[str] = None,
    width: int = 1920,
    height: int = 1080,
    fps_num: int = 30,
    fps_den: int = 1,
    progressive: bool = True,
    dar_num: int = 16,
    dar_den: int = 9,
) -> Dict[str, Any]:
    """Create a new Kdenlive project (JSON format)."""
    if profile and profile in PROFILES:
        p = PROFILES[profile]
        width = p["width"]
        height = p["height"]
        fps_num = p["fps_num"]
        fps_den = p["fps_den"]
        progressive = p["progressive"]
        dar_num = p["dar_num"]
        dar_den = p["dar_den"]
    elif profile and profile not in PROFILES:
        raise ValueError(
            f"Unknown profile: {profile}. "
            f"Available: {', '.join(PROFILES.keys())}"
        )

    if width < 1 or height < 1:
        raise ValueError(f"Resolution must be positive: {width}x{height}")
    if fps_num < 1 or fps_den < 1:
        raise ValueError(f"FPS numerator and denominator must be positive: {fps_num}/{fps_den}")
    if dar_num < 1 or dar_den < 1:
        raise ValueError(f"Display aspect ratio must be positive: {dar_num}:{dar_den}")

    profile_name = profile if profile else "custom"

    project = {
        "version": PROJECT_VERSION,
        "name": name,
        "profile": {
            "name": profile_name,
            "width": width,
            "height": height,
            "fps_num": fps_num,
            "fps_den": fps_den,
            "progressive": progressive,
            "dar_num": dar_num,
            "dar_den": dar_den,
        },
        "bin": [],
        "tracks": [],
        "transitions": [],
        "guides": [],
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "software": "kdenlive-cli 1.0",
        },
    }
    return project


def open_project(path: str) -> Dict[str, Any]:
    """Open a .kdenlive-cli.json project file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Project file not found: {path}")
    with open(path, "r") as f:
        project = json.load(f)
    if "version" not in project or "profile" not in project:
        raise ValueError(f"Invalid project file: {path}")
    return project


def save_project(project: Dict[str, Any], path: str) -> str:
    """Save project to a .kdenlive-cli.json file."""
    project["metadata"]["modified"] = datetime.now().isoformat()
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w") as f:
        json.dump(project, f, indent=2, default=str)
    return path


def get_project_info(project: Dict[str, Any]) -> Dict[str, Any]:
    """Get summary information about the project."""
    profile = project.get("profile", {})
    fps = profile.get("fps_num", 30) / max(profile.get("fps_den", 1), 1)
    bin_clips = project.get("bin", [])
    tracks = project.get("tracks", [])
    transitions = project.get("transitions", [])
    guides = project.get("guides", [])

    total_clips_on_tracks = sum(len(t.get("clips", [])) for t in tracks)

    return {
        "name": project.get("name", "untitled"),
        "version": project.get("version", "unknown"),
        "profile": {
            "name": profile.get("name", "custom"),
            "resolution": f"{profile.get('width', 0)}x{profile.get('height', 0)}",
            "fps": round(fps, 3),
            "progressive": profile.get("progressive", True),
            "aspect_ratio": f"{profile.get('dar_num', 16)}:{profile.get('dar_den', 9)}",
        },
        "counts": {
            "bin_clips": len(bin_clips),
            "tracks": len(tracks),
            "clips_on_timeline": total_clips_on_tracks,
            "transitions": len(transitions),
            "guides": len(guides),
        },
        "bin": [
            {"id": c["id"], "name": c.get("name", ""), "type": c.get("type", "video")}
            for c in bin_clips
        ],
        "tracks": [
            {"id": t["id"], "name": t.get("name", ""), "type": t.get("type", "video"),
             "clips": len(t.get("clips", []))}
            for t in tracks
        ],
        "metadata": project.get("metadata", {}),
    }


