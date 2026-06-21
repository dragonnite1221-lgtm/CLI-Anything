# ruff: noqa: F403, F405, E501
from .motion_base import *  # noqa: F403


def _now_iso() -> str:
    return datetime.now().isoformat()


def _next_id(project: Dict[str, Any]) -> int:
    items = ensure_collection(project, _COLLECTION_KEY)
    if not items:
        return 1
    return max(int(item["id"]) for item in items) + 1


def _unique_name(project: Dict[str, Any], base: str) -> str:
    items = ensure_collection(project, _COLLECTION_KEY)
    existing = {item["name"] for item in items}
    if base not in existing:
        return base
    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _validate_vec3(value: Optional[List[float]], label: str) -> Optional[List[float]]:
    if value is None:
        return None
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{label} must be a list of 3 numbers")
    try:
        return [float(component) for component in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} elements must be numeric: {exc}") from exc


def _validate_time(value: float, duration: float) -> float:
    numeric = float(value)
    if numeric < 0.0 or numeric > float(duration):
        raise ValueError(f"time must be within [0, {duration}], got {numeric}")
    return numeric


def _validate_motion_index(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    items = ensure_collection(project, _COLLECTION_KEY)
    if not isinstance(index, int) or index < 0 or index >= len(items):
        raise IndexError(f"Motion index {index} out of range (0..{len(items) - 1})")
    return items[index]


def _track_summary(track: Dict[str, Any]) -> Dict[str, Any]:
    keyframes = track.get("keyframes", [])
    return {
        "target": dict(track.get("target", {})),
        "keyframe_count": len(keyframes),
        "time_range": [
            float(keyframes[0]["time"]) if keyframes else 0.0,
            float(keyframes[-1]["time"]) if keyframes else 0.0,
        ],
    }


def _normalize_target(
    project: Dict[str, Any], target_kind: str, target_index: int
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if target_kind not in TARGET_KINDS:
        raise ValueError(
            f"Unsupported target_kind '{target_kind}'. Valid: {', '.join(sorted(TARGET_KINDS))}"
        )
    if target_kind == "part":
        part = get_part(project, target_index)
        return (
            {
                "kind": "part",
                "index": int(target_index),
                "part_id": int(part["id"]),
                "name": part["name"],
            },
            part,
        )
    raise ValueError(f"Unsupported target_kind '{target_kind}'")


def _resolve_target_part(
    project: Dict[str, Any], target: Dict[str, Any]
) -> Dict[str, Any]:
    if target.get("kind") != "part":
        raise ValueError(f"Unsupported motion target: {target}")
    parts = project.get("parts", [])
    index = int(target.get("index", -1))
    part_id = target.get("part_id")
    if 0 <= index < len(parts) and parts[index].get("id") == part_id:
        return parts[index]
    for part in parts:
        if part.get("id") == part_id:
            return part
    raise ValueError(f"Motion target part could not be resolved: {target}")


def _find_track(
    motion: Dict[str, Any], target: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    for track in motion.get("tracks", []):
        existing = track.get("target", {})
        if existing.get("kind") == target.get("kind") and existing.get(
            "part_id"
        ) == target.get("part_id"):
            return track
    return None


def _sorted_keyframes(keyframes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        keyframes,
        key=lambda item: (float(item["time"]), json.dumps(item, sort_keys=True)),
    )


def _interpolate_vec3(a: List[float], b: List[float], alpha: float) -> List[float]:
    return [float(a[i]) + (float(b[i]) - float(a[i])) * alpha for i in range(3)]


def _track_state_at_time(track: Dict[str, Any], time_value: float) -> Dict[str, Any]:
    keyframes = _sorted_keyframes(track.get("keyframes", []))
    if not keyframes:
        raise ValueError(f"Track has no keyframes: {track.get('target')}")

    if time_value <= float(keyframes[0]["time"]):
        first = keyframes[0]
        return {
            "position": list(first["position"]),
            "rotation": list(first["rotation"]),
        }
    if time_value >= float(keyframes[-1]["time"]):
        last = keyframes[-1]
        return {
            "position": list(last["position"]),
            "rotation": list(last["rotation"]),
        }

    for left, right in zip(keyframes, keyframes[1:]):
        left_time = float(left["time"])
        right_time = float(right["time"])
        if left_time <= time_value <= right_time:
            if right_time == left_time:
                alpha = 0.0
            else:
                alpha = (time_value - left_time) / (right_time - left_time)
            return {
                "position": _interpolate_vec3(
                    left["position"], right["position"], alpha
                ),
                "rotation": _interpolate_vec3(
                    left["rotation"], right["rotation"], alpha
                ),
            }
    last = keyframes[-1]
    return {
        "position": list(last["position"]),
        "rotation": list(last["rotation"]),
    }


def _frame_times(duration: float, fps: int) -> List[float]:
    if fps <= 0:
        raise ValueError("fps must be positive")
    frame_count = max(2, int(round(float(duration) * int(fps))) + 1)
    return [min(float(duration), i / float(fps)) for i in range(frame_count)]


def _safe_path(path: str) -> str:
    return path.replace("\\", "/")
