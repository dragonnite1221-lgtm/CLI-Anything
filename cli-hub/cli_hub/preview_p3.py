# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import _coalesce, _normalize_index, _stringify_command  # noqa: E402,E501
from .preview_p2 import _extract_bundle_payload  # noqa: E402,E501
# fmt: on


def _normalize_timeline_row(item: Any, index: int) -> Dict[str, Any]:
    if not isinstance(item, dict):
        return {
            "order_index": index,
            "step_index": index,
            "step_id": f"step-{index:03d}",
            "step_label": str(item),
            "command": None,
            "command_started_at": None,
            "command_finished_at": None,
            "timeline_ready_at": None,
            "publish_reason": None,
            "bundle_id": None,
            "bundle_dir": None,
            "manifest_path": None,
            "summary_path": None,
            "status": None,
            "stage_label": None,
            "note": None,
        }

    bundle = _extract_bundle_payload(item)
    command = _stringify_command(
        _coalesce(
            item.get("command"),
            item.get("display_cmd"),
            item.get("display_command"),
            item.get("argv"),
            item.get("raw_command"),
        )
    )
    step_index = _normalize_index(
        _coalesce(item.get("step_index"), item.get("index"), item.get("sequence_index")),
        index,
    )
    status = item.get("status")
    if status is None and "returncode" in item:
        status = "ok" if int(item.get("returncode", 1)) == 0 else "error"

    return {
        "order_index": index,
        "step_index": step_index,
        "step_id": str(
            _coalesce(item.get("step_id"), item.get("id"), item.get("command_id"), f"step-{step_index:03d}")
        ),
        "step_label": _coalesce(
            item.get("step_label"),
            item.get("label"),
            item.get("title"),
            item.get("name"),
            item.get("stage_title"),
            item.get("stage_label"),
        ),
        "command": command,
        "command_started_at": _coalesce(
            item.get("command_started_at"),
            item.get("started_at"),
            item.get("timeline_start_s"),
            item.get("start_s"),
        ),
        "command_finished_at": _coalesce(
            item.get("command_finished_at"),
            item.get("finished_at"),
            item.get("timeline_end_s"),
            item.get("end_s"),
            item.get("completed_at"),
        ),
        "timeline_ready_at": _coalesce(
            item.get("timeline_ready_s"),
            item.get("ready_at"),
            item.get("published_at"),
            item.get("created_at"),
        ),
        "publish_reason": _coalesce(item.get("publish_reason"), item.get("reason")),
        "bundle_id": _coalesce(item.get("bundle_id"), bundle.get("bundle_id")),
        "bundle_dir": _coalesce(item.get("bundle_dir"), bundle.get("bundle_dir")),
        "manifest_path": _coalesce(item.get("manifest_path"), bundle.get("manifest_path")),
        "summary_path": _coalesce(item.get("summary_path"), bundle.get("summary_path")),
        "status": status,
        "stage_label": _coalesce(
            item.get("stage_title"),
            item.get("stage_label"),
            item.get("stage_id"),
            item.get("stage"),
        ),
        "note": _coalesce(
            item.get("note"),
            item.get("stage_story"),
            item.get("story"),
            item.get("description"),
        ),
    }
def _merge_timeline_rows(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    for key in (
        "step_label",
        "command",
        "command_started_at",
        "command_finished_at",
        "timeline_ready_at",
        "publish_reason",
        "bundle_id",
        "bundle_dir",
        "manifest_path",
        "summary_path",
        "status",
        "stage_label",
        "note",
    ):
        target[key] = _coalesce(target.get(key), source.get(key))
def _pick_trajectory_events(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("preview_events", "events", "publishes", "entries", "history", "steps", "timeline"):
        value = raw.get(key)
        if isinstance(value, list) and value:
            return value
    return []
def _sort_timeline_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def sort_key(row: Dict[str, Any]) -> Tuple[int, int, str]:
        step_index = _normalize_index(row.get("step_index"), row.get("order_index", 0))
        order_index = _normalize_index(row.get("order_index"), step_index)
        finish = _coalesce(row.get("command_finished_at"), row.get("timeline_ready_at"), "")
        return step_index, order_index, str(finish)

    return sorted(rows, key=sort_key)
