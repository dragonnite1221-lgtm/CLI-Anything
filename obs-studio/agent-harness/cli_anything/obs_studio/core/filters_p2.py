# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p1 import _get_source_filters  # noqa: E402,E501
# fmt: on


def list_filters(
    project: Dict[str, Any],
    source_index: int,
    scene_index: int = 0,
) -> List[Dict[str, Any]]:
    """List all filters on a source."""
    filters = _get_source_filters(project, source_index, scene_index)
    return [
        {
            "index": i,
            "id": f.get("id", i),
            "name": f.get("name", f"Filter {i}"),
            "type": f.get("type", "unknown"),
            "enabled": f.get("enabled", True),
        }
        for i, f in enumerate(filters)
    ]


def list_available_filters(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all available filter types."""
    result = []
    for name, spec in FILTER_TYPES.items():
        if category and spec.get("category") != category:
            continue
        result.append(
            {
                "name": name,
                "label": spec["label"],
                "category": spec["category"],
                "params": list(spec["params"].keys()),
            }
        )
    return result
