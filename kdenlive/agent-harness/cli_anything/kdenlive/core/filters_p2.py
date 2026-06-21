# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


def set_filter_param(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
    filter_index: int,
    param_name: str,
    value: Any,
) -> Dict[str, Any]:
    """Set a parameter on a filter."""
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
        raise IndexError(f"Filter index {filter_index} out of range.")

    filt = filters[filter_index]
    fname = filt["name"]
    spec = FILTER_REGISTRY.get(fname, {})
    param_specs = spec.get("params", {})

    if param_name not in param_specs:
        raise ValueError(
            f"Unknown parameter '{param_name}' for filter '{fname}'. "
            f"Valid: {', '.join(param_specs.keys())}"
        )

    pspec = param_specs[param_name]
    ptype = pspec["type"]
    if ptype == "float":
        value = float(value)
        if value < pspec["min"] or value > pspec["max"]:
            raise ValueError(
                f"Parameter '{param_name}' value {value} out of range "
                f"[{pspec['min']}, {pspec['max']}]."
            )
    elif ptype == "int":
        value = int(value)
        if value < pspec["min"] or value > pspec["max"]:
            raise ValueError(
                f"Parameter '{param_name}' value {value} out of range "
                f"[{pspec['min']}, {pspec['max']}]."
            )

    filt["params"][param_name] = value
    return dict(filt)


def list_filters(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
) -> List[Dict[str, Any]]:
    """List filters on a clip."""
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

    return [
        {
            "index": i,
            "name": f["name"],
            "mlt_service": f.get("mlt_service", ""),
            "params": f.get("params", {}),
            "enabled": f.get("enabled", True),
        }
        for i, f in enumerate(clips[clip_index].get("filters", []))
    ]


def list_available(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all available filters."""
    result = []
    for name, spec in FILTER_REGISTRY.items():
        if category and spec.get("category") != category:
            continue
        result.append(
            {
                "name": name,
                "mlt_service": spec["mlt_service"],
                "category": spec.get("category", ""),
                "params": {
                    k: {"type": v["type"], "default": v["default"]}
                    for k, v in spec["params"].items()
                },
            }
        )
    return result
