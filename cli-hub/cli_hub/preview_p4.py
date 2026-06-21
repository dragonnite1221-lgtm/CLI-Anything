# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import _coalesce, _read_json, _resolve_ref_path  # noqa: E402,E501
from .preview_p2 import _iter_trajectory_hints, _trajectory_candidate_refs  # noqa: E402,E501
from .preview_p3 import _merge_timeline_rows, _normalize_timeline_row, _pick_trajectory_events, _sort_timeline_rows  # noqa: E402,E501
# fmt: on


def _normalize_trajectory(raw: Optional[Dict[str, Any]], *, fallback_history: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    if not raw and not fallback_history:
        return None

    rows: List[Dict[str, Any]] = []
    rows_by_id: Dict[str, Dict[str, Any]] = {}
    rows_by_index: Dict[int, Dict[str, Any]] = {}
    commands = raw.get("commands", []) if isinstance(raw, dict) else []

    if isinstance(commands, list):
        for index, item in enumerate(commands):
            row = _normalize_timeline_row(item, index)
            rows.append(row)
            rows_by_id[row["step_id"]] = row
            rows_by_index[row["step_index"]] = row

    events = _pick_trajectory_events(raw) if isinstance(raw, dict) else []
    if events:
        for index, item in enumerate(events):
            event_row = _normalize_timeline_row(item, index)
            existing = rows_by_id.get(event_row["step_id"]) or rows_by_index.get(event_row["step_index"])
            if existing is None:
                rows.append(event_row)
                rows_by_id[event_row["step_id"]] = event_row
                rows_by_index[event_row["step_index"]] = event_row
                continue
            _merge_timeline_rows(existing, event_row)

    if not rows and fallback_history:
        for index, item in enumerate(fallback_history):
            rows.append(_normalize_timeline_row(item, index))

    rows = _sort_timeline_rows(rows)
    if not rows:
        return None

    recent_command_row = next((row for row in reversed(rows) if row.get("command")), None)
    recent_publish_row = next(
        (row for row in reversed(rows) if row.get("publish_reason") or row.get("bundle_id")),
        None,
    )

    step_count = _coalesce(
        raw.get("step_count") if isinstance(raw, dict) else None,
        len(commands) if isinstance(commands, list) and commands else None,
        len(rows),
    )
    published_bundles = sum(1 for row in rows if row.get("bundle_id"))
    return {
        "protocol": raw.get("protocol") or raw.get("protocol_version") if isinstance(raw, dict) else None,
        "step_count": step_count,
        "current_step_id": _coalesce(
            raw.get("current_step_id") if isinstance(raw, dict) else None,
            recent_publish_row.get("step_id") if recent_publish_row else None,
            recent_command_row.get("step_id") if recent_command_row else None,
        ),
        "published_bundle_count": published_bundles,
        "recent_command": _coalesce(
            raw.get("latest_command") if isinstance(raw, dict) else None,
            recent_command_row.get("command") if recent_command_row else None,
        ),
        "recent_publish_reason": _coalesce(
            raw.get("latest_publish_reason") if isinstance(raw, dict) else None,
            recent_publish_row.get("publish_reason") if recent_publish_row else None,
        ),
        "recent_bundle_id": recent_publish_row.get("bundle_id") if recent_publish_row else None,
        "entries": rows,
    }
def _load_trajectory(base_dir: Path, *payloads: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for ref in _trajectory_candidate_refs(base_dir, *payloads):
        candidate = _resolve_ref_path(base_dir, ref)
        if candidate.is_file():
            raw = _read_json(candidate)
            normalized = _normalize_trajectory(raw)
            if normalized is not None:
                normalized["mode"] = "trajectory"
                normalized["source_path"] = str(candidate)
                normalized["source_label"] = os.path.relpath(candidate, base_dir)
                return normalized

    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for kind, value, label in _iter_trajectory_hints(payload):
            if kind != "object" or not isinstance(value, dict):
                continue
            normalized = _normalize_trajectory(value)
            if normalized is not None:
                normalized["mode"] = "trajectory"
                normalized["source_path"] = None
                normalized["source_label"] = label
                return normalized
    return None
def _history_from_session(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    history = session.get("history", [])
    if not isinstance(history, list) or not history:
        return None
    normalized = _normalize_trajectory({}, fallback_history=history)
    if normalized is None:
        return None
    source_state = session.get("source_state", {}) if isinstance(session.get("source_state"), dict) else {}
    normalized["mode"] = "legacy-history"
    normalized["source_path"] = None
    normalized["source_label"] = "session.history"
    normalized["current_step_id"] = _coalesce(
        session.get("current_step_id"),
        normalized.get("current_step_id"),
    )
    normalized["recent_command"] = _coalesce(
        session.get("latest_command"),
        normalized.get("recent_command"),
    )
    normalized["recent_publish_reason"] = _coalesce(
        session.get("latest_publish_reason"),
        normalized.get("recent_publish_reason"),
        source_state.get("last_publish_reason"),
    )
    return normalized
