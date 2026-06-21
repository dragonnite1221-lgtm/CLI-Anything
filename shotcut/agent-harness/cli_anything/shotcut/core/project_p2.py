# ruff: noqa: F403, F405, E501
from .project_base import *  # noqa: F403

# fmt: off
from .project_p1 import _get_media_producers  # noqa: E402,E501
# fmt: on


def project_info(session: Session) -> dict:
    """Get detailed info about the current project.

    Returns:
        Dict with comprehensive project info
    """
    if not session.is_open:
        raise RuntimeError("No project is open")

    profile = session.get_profile()
    root = session.root

    media_producers = []
    for p in _get_media_producers(root):
        media_producers.append(
            {
                "id": p.get("id"),
                "resource": mlt_xml.get_property(p, "resource", ""),
                "caption": mlt_xml.get_property(p, "shotcut:caption", ""),
                "in": p.get("in", ""),
                "out": p.get("out", ""),
                "service": mlt_xml.get_property(p, "mlt_service") or "avformat",
            }
        )

    # Tracks
    tracks_info = []
    try:
        tractor = session.get_main_tractor()
        track_elements = mlt_xml.get_tractor_tracks(tractor)
        for i, te in enumerate(track_elements):
            producer_id = te.get("producer", "")
            hide = te.get("hide", "")
            playlist = mlt_xml.find_element_by_id(root, producer_id)

            track_data = {
                "index": i,
                "playlist_id": producer_id,
                "hide": hide,
            }

            if playlist is not None:
                track_data["name"] = mlt_xml.get_property(playlist, "shotcut:name", "")
                is_video = mlt_xml.get_property(playlist, "shotcut:video")
                is_audio = mlt_xml.get_property(playlist, "shotcut:audio")
                if is_video:
                    track_data["type"] = "video"
                elif is_audio or hide == "video":
                    track_data["type"] = "audio"
                elif producer_id == "background":
                    track_data["type"] = "background"
                else:
                    track_data["type"] = "video"

                entries = mlt_xml.get_playlist_entries(playlist)
                from .timeline import real_clip_entries

                track_data["clip_count"] = len(real_clip_entries(entries, root))
                track_data["blank_count"] = sum(
                    1 for e in entries if e["type"] == "blank"
                )
            else:
                track_data["type"] = "unknown"
                track_data["clip_count"] = 0

            tracks_info.append(track_data)
    except RuntimeError:
        pass

    # Filters on main tractor
    filters_info = []
    try:
        tractor = session.get_main_tractor()
        for f in tractor.findall("filter"):
            filters_info.append(
                {
                    "id": f.get("id"),
                    "service": mlt_xml.get_property(f, "mlt_service", ""),
                }
            )
    except RuntimeError:
        pass

    return {
        "project_path": session.project_path,
        "modified": session.is_modified,
        "profile": profile,
        "media_clips": media_producers,
        "tracks": tracks_info,
        "global_filters": filters_info,
    }


def list_profiles() -> dict:
    """List all available video profiles."""
    result = {}
    for name, prof in sorted(PROFILES.items()):
        fps_num = int(prof["frame_rate_num"])
        fps_den = int(prof["frame_rate_den"])
        fps = round(fps_num / fps_den, 2)
        result[name] = {
            "resolution": f"{prof['width']}x{prof['height']}",
            "fps": fps,
            "colorspace": prof.get("colorspace", "709"),
        }
    return result
