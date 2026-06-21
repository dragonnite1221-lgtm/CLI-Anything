# ruff: noqa: F403, F405, E501
from .media_base import *  # noqa: F403

# fmt: off
from .media_p1 import list_media, probe_media  # noqa: E402,E501
# fmt: on


def import_media(session: Session, resource: str, caption: str | None = None) -> dict:
    """Import a media file into the project bin.

    If the file is already imported, returns the existing clip_id.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")

    resource = os.path.abspath(resource)
    if not os.path.isfile(resource):
        raise FileNotFoundError(f"Media file not found: {resource}")

    existing_id = session._clip_resources.get(resource)
    if existing_id is not None:
        chain = session._bin_chains.get(existing_id)
        return {
            "action": "import_media",
            "clip_id": existing_id,
            "source": resource,
            "already_imported": True,
            "caption": mlt_xml.get_property(chain, "shotcut:caption", "")
            if chain is not None
            else "",
        }

    info = probe_media(resource)

    has_video = bool(info.get("video_streams"))
    has_audio = bool(info.get("audio_streams"))
    video_index = "0" if has_video else "-1"
    audio_index = "1" if has_audio and has_video else ("0" if has_audio else "-1")
    if not has_video and not has_audio:
        video_index, audio_index = "0", "1"

    from ..utils.time import frames_to_timecode
    from .timeline import _get_fps

    fps_num, fps_den = _get_fps(session)
    duration = info.get("duration_seconds", 0)
    if duration > 0:
        out_point = frames_to_timecode(
            round(duration * fps_num / fps_den), fps_num, fps_den
        )
        length_tc = frames_to_timecode(
            round(duration * fps_num / fps_den) + 1, fps_num, fps_den
        )
    else:
        out_point = None
        length_tc = None

    clip_id = f"clip{session._clip_id_counter}"
    session._clip_id_counter += 1

    session.checkpoint()

    extra = {"video_index": video_index, "audio_index": audio_index}

    bin_chain = mlt_xml.create_chain(
        session.root,
        resource,
        in_point="00:00:00.000",
        out_point=out_point,
        caption=caption or os.path.basename(resource),
        extra_props=extra,
        insert_idx=session._bin_insert_idx,
        length=length_tc,
    )
    session._bin_insert_idx += 1
    mlt_xml.add_chain_to_bin(session.root, bin_chain)

    session._bin_chains[clip_id] = bin_chain
    session._clip_ids[clip_id] = resource
    session._clip_resources[resource] = clip_id

    return {
        "action": "import_media",
        "clip_id": clip_id,
        "source": resource,
        "caption": caption or os.path.basename(resource),
        "duration": duration,
        "video_streams": len(info.get("video_streams", [])),
        "audio_streams": len(info.get("audio_streams", [])),
    }


def get_clip_info(session: Session, clip_id: str) -> dict:
    """Get info about an imported clip."""
    chain = session._bin_chains.get(clip_id)
    if chain is None:
        available = ", ".join(sorted(session._bin_chains.keys()))
        raise ValueError(f"Clip {clip_id!r} not found. Available: {available}")
    resource = mlt_xml.get_property(chain, "resource", "")
    return {
        "clip_id": clip_id,
        "resource": resource,
        "caption": mlt_xml.get_property(chain, "shotcut:caption", ""),
        "in": chain.get("in", ""),
        "out": chain.get("out", ""),
    }


def check_media_files(session: Session) -> dict:
    """Check all media files in the project for existence.

    Returns:
        Dict with lists of found and missing files
    """
    media = list_media(session)
    found = []
    missing = []

    for m in media:
        if m["exists"]:
            found.append(m["resource"])
        else:
            missing.append(m["resource"])

    return {
        "total": len(media),
        "found": found,
        "missing": missing,
        "all_present": len(missing) == 0,
    }
