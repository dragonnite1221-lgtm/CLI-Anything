# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


def _validate_filter_params(filter_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fill defaults for filter parameters."""
    spec = FILTER_REGISTRY[filter_name]
    param_specs = spec["params"]

    unknown = set(params.keys()) - set(param_specs.keys())
    if unknown:
        raise ValueError(
            f"Unknown parameters for '{filter_name}': {', '.join(unknown)}. "
            f"Valid: {', '.join(param_specs.keys())}"
        )

    result = {}
    for pname, pspec in param_specs.items():
        value = params.get(pname, pspec["default"])
        ptype = pspec["type"]

        if ptype == "float":
            value = float(value)
            if value < pspec["min"] or value > pspec["max"]:
                raise ValueError(
                    f"Parameter '{pname}' value {value} out of range "
                    f"[{pspec['min']}, {pspec['max']}]."
                )
        elif ptype == "int":
            value = int(value)
            if value < pspec["min"] or value > pspec["max"]:
                raise ValueError(
                    f"Parameter '{pname}' value {value} out of range "
                    f"[{pspec['min']}, {pspec['max']}]."
                )
        elif ptype == "str":
            value = str(value)

        result[pname] = value

    return result


def add_filter(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
    filter_name: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add a filter to a clip on a track."""
    if filter_name not in FILTER_REGISTRY:
        raise ValueError(
            f"Unknown filter: {filter_name}. "
            f"Available: {', '.join(FILTER_REGISTRY.keys())}"
        )

    tracks = project.get("tracks", [])
    track = None
    for t in tracks:
        if t["id"] == track_id:
            track = t
            break
    if track is None:
        raise ValueError(f"Track not found: {track_id}")

    clips = track.get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range (0-{len(clips) - 1}).")

    validated_params = _validate_filter_params(filter_name, params or {})

    spec = FILTER_REGISTRY[filter_name]
    filter_entry = {
        "name": filter_name,
        "mlt_service": spec["mlt_service"],
        "params": validated_params,
        "enabled": True,
    }

    clips[clip_index].setdefault("filters", []).append(filter_entry)
    return filter_entry


def remove_filter(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
    filter_index: int,
) -> Dict[str, Any]:
    """Remove a filter from a clip."""
    tracks = project.get("tracks", [])
    track = None
    for t in tracks:
        if t["id"] == track_id:
            track = t
            break
    if track is None:
        raise ValueError(f"Track not found: {track_id}")

    clips = track.get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range.")

    filters = clips[clip_index].get("filters", [])
    if filter_index < 0 or filter_index >= len(filters):
        raise IndexError(
            f"Filter index {filter_index} out of range (0-{len(filters) - 1})."
        )

    return filters.pop(filter_index)
