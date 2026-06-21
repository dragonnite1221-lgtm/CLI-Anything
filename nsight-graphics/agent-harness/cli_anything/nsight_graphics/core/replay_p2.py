# ruff: noqa: F403, F405, E501
from .replay_base import *  # noqa: F403
# fmt: off
from .replay_p1 import _first_value, _load_json_artifact, _read_text, _records_from_json, _top_counts  # noqa: E402,E501
# fmt: on


def _summarize_objects(path: Path | None) -> dict[str, Any]:
    """Summarize object metadata from ngfx-replay --metadata-objects."""
    if path is None:
        return {"parsed": False, "total": 0, "top_types": [], "top_apis": []}
    data, error = _load_json_artifact(path)
    records = _records_from_json(data, ("objects", "resources", "items"))
    type_counts: Counter[str] = Counter()
    api_counts: Counter[str] = Counter()
    named_count = 0
    uid_count = 0
    samples: list[dict[str, Any]] = []

    for item in records:
        type_value = _first_value(item, ("type_name", "type", "object_type", "objectType", "resource_type", "resourceType"))
        api_value = _first_value(item, ("api", "graphics_api", "graphicsApi"))
        name_value = _first_value(item, ("object_name", "name", "label"))
        uid_value = _first_value(item, ("uid", "id", "object_id", "objectId"))
        if type_value is not None:
            type_counts[str(type_value)] += 1
        if api_value is not None:
            api_counts[str(api_value)] += 1
        if name_value is not None:
            named_count += 1
        if uid_value is not None:
            uid_count += 1
        if len(samples) < 5:
            samples.append(
                {
                    "uid": uid_value,
                    "type": type_value,
                    "name": name_value,
                    "api": api_value,
                }
            )

    summary: dict[str, Any] = {
        "parsed": bool(records),
        "total": len(records),
        "named_count": named_count,
        "uid_count": uid_count,
        "top_types": _top_counts(type_counts),
        "top_apis": _top_counts(api_counts),
        "samples": samples,
    }
    if error:
        summary["parse_error"] = error
    return summary
def _summarize_functions(path: Path | None) -> dict[str, Any]:
    """Summarize function-stream metadata from ngfx-replay --metadata-functions."""
    if path is None:
        return {"parsed": False, "total": 0, "unique_count": 0, "top_functions": []}

    data, error = _load_json_artifact(path)
    records = _records_from_json(data, ("functions", "events", "items"))
    names: list[str] = []
    thread_ids: set[str] = set()
    sequence_ids: list[int] = []

    for item in records:
        name = _first_value(item, ("function_name", "name", "function", "call"))
        if name is not None:
            names.append(str(name))
        thread_id = _first_value(item, ("thread_index", "thread_id", "threadId"))
        if thread_id is not None:
            thread_ids.add(str(thread_id))
        sequence_id = _first_value(item, ("sequence_id", "sequenceId", "event_index", "eventIndex"))
        if isinstance(sequence_id, int):
            sequence_ids.append(sequence_id)

    fallback_used = False
    if not records and not error:
        lines = [line.strip() for line in _read_text(path).splitlines() if line.strip()]
        if lines:
            fallback_used = True
            names = lines

    counts = Counter(names)
    summary: dict[str, Any] = {
        "parsed": bool(records) or fallback_used,
        "total": len(names),
        "unique_count": len(counts),
        "top_functions": _top_counts(counts),
        "thread_count": len(thread_ids),
    }
    if sequence_ids:
        summary["first_sequence_id"] = min(sequence_ids)
        summary["last_sequence_id"] = max(sequence_ids)
    if error:
        summary["parse_error"] = error
    if fallback_used:
        summary["parse_mode"] = "line_fallback"
    return summary
def _compact_result(kind: str, result: dict[str, Any], *, stdout_file: Path | None = None, output_file: Path | None = None) -> dict[str, Any]:
    """Return a JSON-friendly command result without embedding large stdout blobs."""
    payload: dict[str, Any] = {
        "kind": kind,
        "ok": result.get("ok", False),
        "returncode": result.get("returncode"),
        "command": result.get("command"),
        "stdout_bytes": len((result.get("stdout") or "").encode("utf-8")),
        "stderr": result.get("stderr") or "",
    }
    if stdout_file is not None:
        payload["stdout_file"] = str(stdout_file)
        payload["stdout_file_present"] = stdout_file.is_file() and stdout_file.stat().st_size > 0
    if output_file is not None:
        payload["output_file"] = str(output_file)
        payload["output_file_present"] = output_file.is_file() and output_file.stat().st_size > 0
    return payload
