# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import real_clip_entries  # noqa: E402,E501
# fmt: on


def list_tracks(session: Session) -> list[dict]:
    """List all tracks in the timeline."""
    if not session.is_open:
        raise RuntimeError("No project is open")

    tractor = session.get_main_tractor()
    tracks = mlt_xml.get_tractor_tracks(tractor)
    result = []

    for i, te in enumerate(tracks):
        producer_id = te.get("producer", "")
        playlist = mlt_xml.find_element_by_id(session.root, producer_id)

        info = {
            "index": i,
            "playlist_id": producer_id,
            "hide": te.get("hide", ""),
        }

        if playlist is not None:
            info["name"] = mlt_xml.get_property(playlist, "shotcut:name", "")
            is_video = mlt_xml.get_property(playlist, "shotcut:video")
            is_audio = mlt_xml.get_property(playlist, "shotcut:audio")
            if is_video:
                info["type"] = "video"
            elif is_audio or te.get("hide") == "video":
                info["type"] = "audio"
            elif producer_id == "background":
                info["type"] = "background"
            else:
                info["type"] = "video"

            entries = mlt_xml.get_playlist_entries(playlist)
            info["clip_count"] = len(real_clip_entries(entries, session.root))
        else:
            info["type"] = "unknown"
            info["clip_count"] = 0

        result.append(info)

    return result
