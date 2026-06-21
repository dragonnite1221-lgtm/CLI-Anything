# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403


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
            {
                "id": t["id"],
                "name": t.get("name", ""),
                "type": t.get("type", "video"),
                "clips": len(t.get("clips", [])),
            }
            for t in tracks
        ],
        "metadata": project.get("metadata", {}),
    }


def list_profiles() -> List[Dict[str, Any]]:
    """List all available video profiles."""
    result = []
    for name, p in PROFILES.items():
        fps = p["fps_num"] / max(p["fps_den"], 1)
        result.append(
            {
                "name": name,
                "resolution": f"{p['width']}x{p['height']}",
                "fps": round(fps, 3),
                "progressive": p["progressive"],
                "aspect_ratio": f"{p['dar_num']}:{p['dar_den']}",
            }
        )
    return result
