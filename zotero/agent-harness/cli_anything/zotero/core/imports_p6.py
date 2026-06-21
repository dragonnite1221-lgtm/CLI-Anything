# ruff: noqa: F403, F405, E501
from .imports_base import *  # noqa: F403

# fmt: off
from .imports_p1 import _normalize_tags, _read_json_items, _require_connector, _resolve_target, _session_id  # noqa: E402,E501
from .imports_p2 import _extract_inline_attachment_plans  # noqa: E402,E501
from .imports_p4 import _perform_attachment_upload  # noqa: E402,E501
# fmt: on


def import_json(
    runtime: RuntimeContext,
    path: str | Path,
    *,
    collection_ref: str | None = None,
    tags: list[str] | tuple[str, ...] = (),
    session: dict[str, Any] | None = None,
    attachment_delay_ms: int = 0,
    attachment_timeout: int = 60,
) -> dict[str, Any]:
    _require_connector(runtime)
    source_path = Path(path).expanduser()
    if not source_path.exists():
        raise FileNotFoundError(f"Import JSON file not found: {source_path}")
    items = _read_json_items(source_path)
    items, plans = _extract_inline_attachment_plans(
        items,
        default_delay_ms=attachment_delay_ms,
        default_timeout=attachment_timeout,
    )
    session_id = _session_id("import-json")
    zotero_http.connector_save_items(
        runtime.environment.port, items, session_id=session_id
    )
    target = _resolve_target(runtime, collection_ref, session=session)
    normalized_tags = _normalize_tags(list(tags))
    zotero_http.connector_update_session(
        runtime.environment.port,
        session_id=session_id,
        target=target["treeViewID"],
        tags=normalized_tags,
    )
    attachment_summary, attachment_results = _perform_attachment_upload(
        runtime,
        session_id=session_id,
        connector_items=items,
        plans=plans,
    )
    return {
        "action": "import_json",
        "path": str(source_path),
        "status": "partial_success"
        if attachment_summary["failed_count"]
        else "success",
        "sessionID": session_id,
        "target": target,
        "tags": normalized_tags,
        "submitted_count": len(items),
        "items": [
            {
                "id": item.get("id"),
                "itemType": item.get("itemType"),
                "title": item.get("title")
                or item.get("bookTitle")
                or item.get("publicationTitle"),
            }
            for item in items
        ],
        "attachment_summary": attachment_summary,
        "attachment_results": attachment_results,
    }
