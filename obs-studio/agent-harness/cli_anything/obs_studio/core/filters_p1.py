# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403


def _get_source_filters(
    project: Dict[str, Any], source_index: int, scene_index: int = 0
) -> List[Dict[str, Any]]:
    """Get the filter list for a source."""
    scenes = project.get("scenes", [])
    scene = get_item(scenes, scene_index, "scene")
    sources = scene.get("sources", [])
    source = get_item(sources, source_index, "source")
    return source.setdefault("filters", [])


def _validate_filter_params(filter_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fill defaults for filter parameters."""
    spec = FILTER_TYPES[filter_type]
    param_specs = spec["params"]

    # Check for unknown params
    unknown = set(params.keys()) - set(param_specs.keys())
    if unknown:
        raise ValueError(f"Unknown parameters for {filter_type}: {', '.join(unknown)}")

    result = {}
    for pname, pspec in param_specs.items():
        if pname in params:
            val = params[pname]
            ptype = pspec["type"]
            if ptype == "float":
                val = float(val)
                if "min" in pspec and "max" in pspec:
                    val = validate_range(val, pspec["min"], pspec["max"], pname)
            elif ptype == "int":
                val = int(val)
                if "min" in pspec and "max" in pspec:
                    if val < pspec["min"] or val > pspec["max"]:
                        raise ValueError(
                            f"{pname} must be between {pspec['min']} and {pspec['max']}, got {val}"
                        )
            elif ptype == "str":
                val = str(val)
                if "values" in pspec and val not in pspec["values"]:
                    raise ValueError(
                        f"{pname} must be one of {pspec['values']}, got {val}"
                    )
            elif ptype == "bool":
                if isinstance(val, str):
                    val = val.lower() in ("true", "1", "yes")
                val = bool(val)
            result[pname] = val
        else:
            result[pname] = pspec["default"]
    return result


def add_filter(
    project: Dict[str, Any],
    filter_type: str,
    source_index: int,
    scene_index: int = 0,
    name: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add a filter to a source."""
    if filter_type not in FILTER_TYPES:
        raise ValueError(
            f"Unknown filter type: {filter_type}. Valid: {', '.join(sorted(FILTER_TYPES.keys()))}"
        )

    filters = _get_source_filters(project, source_index, scene_index)
    if name is None:
        name = FILTER_TYPES[filter_type]["label"]
    name = unique_name(name, filters)

    validated_params = _validate_filter_params(filter_type, params or {})

    filt = {
        "id": generate_id(filters),
        "name": name,
        "type": filter_type,
        "enabled": True,
        "params": validated_params,
    }
    filters.append(filt)
    return filt


def remove_filter(
    project: Dict[str, Any],
    filter_index: int,
    source_index: int,
    scene_index: int = 0,
) -> Dict[str, Any]:
    """Remove a filter from a source."""
    filters = _get_source_filters(project, source_index, scene_index)
    filt = get_item(filters, filter_index, "filter")
    return filters.pop(filter_index)


def set_filter_param(
    project: Dict[str, Any],
    filter_index: int,
    param: str,
    value: Any,
    source_index: int,
    scene_index: int = 0,
) -> Dict[str, Any]:
    """Set a parameter on a filter."""
    filters = _get_source_filters(project, source_index, scene_index)
    filt = get_item(filters, filter_index, "filter")

    filter_type = filt["type"]
    spec = FILTER_TYPES.get(filter_type)
    if not spec:
        raise ValueError(f"Unknown filter type: {filter_type}")

    param_specs = spec["params"]
    if param not in param_specs:
        raise ValueError(
            f"Unknown parameter '{param}' for filter type '{filter_type}'. Valid: {', '.join(param_specs.keys())}"
        )

    # Validate the single param
    validated = _validate_filter_params(filter_type, {param: value})
    filt["params"][param] = validated[param]
    return filt
