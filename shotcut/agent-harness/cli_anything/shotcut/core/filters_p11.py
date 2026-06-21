# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p9 import _resolve_target  # noqa: E402,E501
from .filters_p10 import _find_filter_index  # noqa: E402,E501
# fmt: on


def set_volume_envelope(
    session: Session,
    points: list[tuple[str, str]],
    *,
    track_index: Optional[int] = None,
    clip_index: Optional[int] = None,
) -> dict:
    if not points:
        raise ValueError("At least one time=level point is required")

    session.checkpoint()
    fps_num, fps_den = (
        int(session.get_profile()["frame_rate_num"]),
        int(session.get_profile()["frame_rate_den"]),
    )

    normalized: dict[int, str] = {}
    for timecode, level in points:
        float(level)
        normalized[parse_time_input(timecode, fps_num, fps_den)] = str(level)

    envelope = ";".join(
        f"{frames_to_timecode(frame, fps_num, fps_den)}={level}"
        for frame, level in sorted(normalized.items())
    )

    target = _resolve_target(session, track_index, clip_index)
    filter_index, filt = _find_filter_index(target, "volume")
    if filt is None:
        filt = mlt_xml.add_filter_to_element(
            target, "volume", properties={"level": envelope}
        )
        filter_index = len(target.findall("filter")) - 1
        old_value = None
    else:
        old_value = mlt_xml.get_property(filt, "level")
        mlt_xml.set_property(filt, "level", envelope)

    return {
        "action": "set_volume_envelope",
        "filter_index": filter_index,
        "service": "volume",
        "old_value": old_value,
        "level": envelope,
    }


def duck_volume(
    session: Session,
    windows: list[tuple[str, str]],
    *,
    track_index: Optional[int] = None,
    clip_index: Optional[int] = None,
    normal_level: float = 1.0,
    duck_level: float = 0.25,
    attack: str = "00:00:00.150",
    release: str = "00:00:00.250",
) -> dict:
    if not windows:
        raise ValueError("At least one ducking window is required")

    fps_num, fps_den = (
        int(session.get_profile()["frame_rate_num"]),
        int(session.get_profile()["frame_rate_den"]),
    )
    attack_frames = parse_time_input(attack, fps_num, fps_den)
    release_frames = parse_time_input(release, fps_num, fps_den)

    frame_points: dict[int, str] = {0: str(normal_level)}
    sorted_windows = sorted(
        windows, key=lambda item: parse_time_input(item[0], fps_num, fps_den)
    )
    for start_tc, end_tc in sorted_windows:
        start_frame = parse_time_input(start_tc, fps_num, fps_den)
        end_frame = parse_time_input(end_tc, fps_num, fps_den)
        if end_frame < start_frame:
            raise ValueError(f"Invalid ducking window: {start_tc}:{end_tc}")

        frame_points[max(0, start_frame - attack_frames)] = str(normal_level)
        frame_points[start_frame] = str(duck_level)
        frame_points[end_frame] = str(duck_level)
        frame_points[end_frame + release_frames] = str(normal_level)

    result = set_volume_envelope(
        session,
        [
            (frames_to_timecode(frame, fps_num, fps_den), level)
            for frame, level in sorted(frame_points.items())
        ],
        track_index=track_index,
        clip_index=clip_index,
    )
    result.update(
        {
            "action": "duck_volume",
            "windows": sorted_windows,
            "normal_level": normal_level,
            "duck_level": duck_level,
            "attack": attack,
            "release": release,
        }
    )
    return result
