# ruff: noqa: F403, F405, E501
from .filters_base import *  # noqa: F403

# fmt: off
from .filters_p9 import _resolve_target  # noqa: E402,E501
# fmt: on


def remove_filter(
    session: Session,
    filter_index: int,
    track_index: Optional[int] = None,
    clip_index: Optional[int] = None,
) -> dict:
    """Remove a filter by index from a target element.

    Args:
        filter_index: Index of the filter among filters on the target
        track_index: Track (None = global/tractor filters)
        clip_index: Clip (None = track-level filters)
    """
    session.checkpoint()
    target = _resolve_target(session, track_index, clip_index)

    filters = target.findall("filter")
    if filter_index < 0 or filter_index >= len(filters):
        raise IndexError(
            f"Filter index {filter_index} out of range (0-{len(filters) - 1})"
        )

    filt = filters[filter_index]
    filter_id = filt.get("id")
    service = mlt_xml.get_property(filt, "mlt_service", "")
    target.remove(filt)

    return {
        "action": "remove_filter",
        "filter_index": filter_index,
        "filter_id": filter_id,
        "service": service,
    }


def set_filter_param(
    session: Session,
    filter_index: int,
    param_name: str,
    param_value: str,
    track_index: Optional[int] = None,
    clip_index: Optional[int] = None,
) -> dict:
    """Set a parameter on a filter.

    Args:
        filter_index: Index of the filter on the target
        param_name: Property name to set
        param_value: New value
        track_index: Track (None = global)
        clip_index: Clip (None = track-level)
    """
    session.checkpoint()
    target = _resolve_target(session, track_index, clip_index)

    filters = target.findall("filter")
    if filter_index < 0 or filter_index >= len(filters):
        raise IndexError(f"Filter index {filter_index} out of range")

    filt = filters[filter_index]
    old_value = mlt_xml.get_property(filt, param_name)
    mlt_xml.set_property(filt, param_name, param_value)

    return {
        "action": "set_filter_param",
        "filter_index": filter_index,
        "param": param_name,
        "old_value": old_value,
        "new_value": param_value,
    }


def list_filters(
    session: Session,
    track_index: Optional[int] = None,
    clip_index: Optional[int] = None,
) -> list[dict]:
    """List all filters on a target element.

    Args:
        track_index: Track (None = global/tractor filters)
        clip_index: Clip (None = track-level filters)
    """
    target = _resolve_target(session, track_index, clip_index)
    filters = target.findall("filter")

    result = []
    for i, filt in enumerate(filters):
        service = mlt_xml.get_property(filt, "mlt_service", "")
        # Get all properties
        props = {}
        for prop in filt.findall("property"):
            name = prop.get("name", "")
            if name and name != "mlt_service":
                props[name] = prop.text or ""

        result.append(
            {
                "index": i,
                "id": filt.get("id"),
                "service": service,
                "params": props,
            }
        )

    return result


def _find_filter_index(
    target: ET.Element, service: str
) -> tuple[int | None, ET.Element | None]:
    for index, filt in enumerate(target.findall("filter")):
        if mlt_xml.get_property(filt, "mlt_service", "") == service:
            return index, filt
    return None, None
