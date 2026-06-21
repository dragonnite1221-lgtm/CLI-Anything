# ruff: noqa: F403, F405, E501
from .motion_base import *  # noqa: F403

# fmt: off
from .motion_p1 import _find_track, _frame_times, _normalize_target, _now_iso, _resolve_target_part, _sorted_keyframes, _track_state_at_time, _track_summary, _validate_motion_index, _validate_time, _validate_vec3  # noqa: E402,E501
# fmt: on


def add_keyframe(
    project: Dict[str, Any],
    motion_index: int,
    *,
    target_kind: str,
    target_index: int,
    time_value: float,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Insert or replace a keyframe on a motion track."""
    motion = _validate_motion_index(project, motion_index)
    target, source_obj = _normalize_target(project, target_kind, target_index)
    placement = source_obj.get("placement", {})
    resolved_position = _validate_vec3(position, "position") or list(
        placement.get("position", [0.0, 0.0, 0.0])
    )
    resolved_rotation = _validate_vec3(rotation, "rotation") or list(
        placement.get("rotation", [0.0, 0.0, 0.0])
    )
    keyframe = {
        "time": _validate_time(time_value, float(motion["duration"])),
        "position": resolved_position,
        "rotation": resolved_rotation,
    }

    track = _find_track(motion, target)
    if track is None:
        track = {"target": target, "keyframes": []}
        motion["tracks"].append(track)

    replaced = False
    updated_keyframes: List[Dict[str, Any]] = []
    for existing in track["keyframes"]:
        if math.isclose(float(existing["time"]), keyframe["time"], abs_tol=1e-9):
            updated_keyframes.append(keyframe)
            replaced = True
        else:
            updated_keyframes.append(existing)
    if not replaced:
        updated_keyframes.append(keyframe)

    track["keyframes"] = _sorted_keyframes(updated_keyframes)
    motion["metadata"]["modified"] = _now_iso()
    return {
        "motion": motion["name"],
        "track": _track_summary(track),
        "keyframe": keyframe,
        "replaced": replaced,
    }


def sample_motion(
    project: Dict[str, Any], motion_index: int, time_value: float
) -> Dict[str, Any]:
    """Evaluate a motion sequence at an arbitrary time."""
    motion = _validate_motion_index(project, motion_index)
    resolved_time = _validate_time(time_value, float(motion["duration"]))
    placements = []
    for track in motion.get("tracks", []):
        state = _track_state_at_time(track, resolved_time)
        placements.append(
            {
                "target": dict(track["target"]),
                "position": state["position"],
                "rotation": state["rotation"],
            }
        )
    return {
        "motion": motion["name"],
        "time": resolved_time,
        "camera": motion["camera"],
        "placements": placements,
    }


def apply_motion(
    project: Dict[str, Any], motion_index: int, time_value: float
) -> Dict[str, Any]:
    """Return a deep-copied project with interpolated placements applied."""
    sampled = sample_motion(project, motion_index, time_value)
    project_copy = copy.deepcopy(project)
    for placement in sampled["placements"]:
        target = placement["target"]
        if target["kind"] != "part":
            continue
        part = _resolve_target_part(project_copy, target)
        part.setdefault("placement", {})
        part["placement"]["position"] = list(placement["position"])
        part["placement"]["rotation"] = list(placement["rotation"])
    return project_copy


def _motion_frames(
    project: Dict[str, Any], motion: Dict[str, Any], output_dir: str
) -> Dict[str, Any]:
    frames: List[Dict[str, Any]] = []
    unsupported_targets: List[Dict[str, Any]] = []
    unsupported_seen = set()

    times = _frame_times(float(motion["duration"]), int(motion["fps"]))
    for frame_index, time_value in enumerate(times):
        placements: Dict[str, Dict[str, List[float]]] = {}
        for track in motion.get("tracks", []):
            target = dict(track["target"])
            part = _resolve_target_part(project, target)
            render_spec = macro_gen._render_spec_for_part(project, part)
            if render_spec is None:
                signature = (target.get("kind"), target.get("part_id"))
                if signature not in unsupported_seen:
                    unsupported_seen.add(signature)
                    unsupported_targets.append(target)
                continue
            state = _track_state_at_time(track, time_value)
            placements[str(target["part_id"])] = {
                "position": state["position"],
                "rotation": state["rotation"],
            }
        frame_path = os.path.join(output_dir, f"frame_{frame_index:05d}.png")
        frames.append(
            {
                "index": frame_index,
                "time": time_value,
                "path": frame_path,
                "placements": placements,
            }
        )
    return {
        "frames": frames,
        "unsupported_targets": unsupported_targets,
    }
