# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403


def xml_escape(s: str) -> str:
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&apos;")
    return s
def _add_prop(parent: ET.Element, name: str, value) -> ET.Element:
    prop = ET.SubElement(parent, "property")
    prop.set("name", name)
    prop.text = str(value)
    return prop
def _add_disabled_filter(parent, service, counter):
    f = ET.SubElement(parent, "filter", {"id": f"filter{counter}"})
    _add_prop(f, "mlt_service", service)
    _add_prop(f, "internal_added", "237")
    _add_prop(f, "disable", "1")
    return counter + 1
def seconds_to_timecode(seconds: float) -> str:
    if seconds < 0:
        raise ValueError(f"Seconds must be non-negative: {seconds}")
    hours = int(seconds // 3600)
    remainder = seconds - hours * 3600
    minutes = int(remainder // 60)
    remainder = remainder - minutes * 60
    secs = int(remainder)
    millis = int(round((remainder - secs) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
def timecode_to_seconds(tc: str) -> float:
    try:
        return float(tc)
    except ValueError:
        pass

    pattern = r'^(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?$'
    m = re.match(pattern, tc)
    if not m:
        raise ValueError(f"Invalid timecode format: {tc}. Expected HH:MM:SS.mmm or seconds.")
    hours = int(m.group(1))
    minutes = int(m.group(2))
    secs = int(m.group(3))
    millis_str = m.group(4) if m.group(4) else "0"
    millis = int(millis_str.ljust(3, '0'))
    return hours * 3600 + minutes * 60 + secs + millis / 1000.0
def seconds_to_frames(seconds: float, fps_num: int = 30, fps_den: int = 1) -> int:
    fps = fps_num / max(fps_den, 1)
    return int(round(seconds * fps))
def frames_to_seconds(frames: int, fps_num: int = 30, fps_den: int = 1) -> float:
    fps = fps_num / max(fps_den, 1)
    return frames / fps
def _compute_track_duration(track: dict, fps_num: int, fps_den: int) -> int:
    max_end = 0.0
    for clip_entry in track.get("clips", []):
        clip_end = clip_entry.get("position", 0.0) + (
            clip_entry.get("out", 0) - clip_entry.get("in", 0)
        )
        max_end = max(max_end, clip_end)
    if max_end <= 0:
        return 0
    return max(seconds_to_frames(max_end, fps_num, fps_den) - 1, 0)
def _clip_type_num(clip_type: str) -> int:
    mapping = {
        "video": 0,
        "audio": 1,
        "image": 2,
        "color": 3,
        "title": 4,
    }
    return mapping.get(clip_type, 0)
def _avformat_indexes(parent: ET.Element, clip_type: str):
    if clip_type == "audio":
        _add_prop(parent, "audio_index", "0")
        _add_prop(parent, "video_index", "-1")
    elif clip_type == "image":
        _add_prop(parent, "audio_index", "-1")
        _add_prop(parent, "video_index", "0")
    else:
        _add_prop(parent, "audio_index", "1")
        _add_prop(parent, "video_index", "0")
def _set_producer_props(parent: ET.Element, clip_type: str):
    if clip_type == "color":
        _add_prop(parent, "mlt_service", "color")
    else:
        _add_prop(parent, "mlt_service", "avformat-novalidate")
        _add_prop(parent, "seekable", "1")
        _avformat_indexes(parent, clip_type)
def _track_index(tracks: list, track_id: int) -> int:
    for i, t in enumerate(tracks):
        if t["id"] == track_id:
            return i
    return 0
_SEQUENCE_FOLDER_ID = "2"
_SEQUENCE_KDENLIVE_ID = "3"
_CLIP_KDENLIVE_ID_START = 4
