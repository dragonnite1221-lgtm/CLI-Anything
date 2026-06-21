# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403


def _get_bin_ids(root):
    main_bin = mlt_xml.find_element_by_id(root, "main_bin")
    if main_bin is None:
        return set()
    return {entry.get("producer", "") for entry in main_bin.findall("entry")}


def _get_media_producers(root):
    bin_ids = _get_bin_ids(root)
    return [
        p
        for p in mlt_xml.get_all_producers(root)
        if mlt_xml.get_property(p, "mlt_service") not in ("color", "colour")
        and mlt_xml.get_property(p, "resource") not in ("0", "")
        and not (p.tag == "chain" and p.get("id", "") not in bin_ids)
    ]


def new_project(session: Session, profile_name: str = "hd1080p30") -> dict:
    """Create a new blank project.

    Args:
        session: The active session
        profile_name: Name of the video profile (see PROFILES)

    Returns:
        Dict with project info
    """
    if profile_name not in PROFILES:
        available = ", ".join(sorted(PROFILES.keys()))
        raise ValueError(f"Unknown profile: {profile_name!r}. Available: {available}")

    profile = PROFILES[profile_name]
    session.new_project(profile)

    return {
        "action": "new_project",
        "profile": profile_name,
        "resolution": f"{profile['width']}x{profile['height']}",
        "fps": f"{profile['frame_rate_num']}/{profile['frame_rate_den']}",
    }


def open_project(session: Session, path: str) -> dict:
    """Open an existing .mlt project file.

    Returns:
        Dict with project info
    """
    session.open_project(path)
    profile = session.get_profile()

    # Count tracks
    try:
        tractor = session.get_main_tractor()
        tracks = mlt_xml.get_tractor_tracks(tractor)
        track_count = len(tracks)
    except RuntimeError:
        track_count = 0

    return {
        "action": "open_project",
        "path": session.project_path,
        "profile": profile,
        "track_count": track_count,
        "media_clip_count": len(_get_media_producers(session.root)),
    }


def save_project(session: Session, path: Optional[str] = None) -> dict:
    """Save the current project.

    Returns:
        Dict with save info
    """
    saved_path = session.save_project(path)
    return {
        "action": "save_project",
        "path": saved_path,
    }
