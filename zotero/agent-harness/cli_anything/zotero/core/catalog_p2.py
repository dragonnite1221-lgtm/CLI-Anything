# ruff: noqa: F403, F405, E501
from .catalog_base import *  # noqa: F403

# fmt: off
from .catalog_p1 import _default_library, _require_sqlite, get_collection, local_api_scope, resolve_library_id  # noqa: E402,E501
# fmt: on


def find_items(
    runtime: RuntimeContext,
    query: str,
    *,
    collection_ref: str | None = None,
    limit: int = 20,
    exact_title: bool = False,
    session: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    sqlite_path = _require_sqlite(runtime)
    collection = None
    if collection_ref:
        collection = get_collection(runtime, collection_ref, session=session)
    library_id = (
        int(collection["libraryID"])
        if collection
        else _default_library(runtime, session)
    )

    if not exact_title and runtime.local_api_available:
        scope = local_api_scope(runtime, library_id)
        path = (
            f"{scope}/collections/{collection['key']}/items/top"
            if collection
            else f"{scope}/items/top"
        )
        payload = zotero_http.local_api_get_json(
            runtime.environment.port,
            path,
            params={"format": "json", "q": query, "limit": limit},
        )
        results: list[dict[str, Any]] = []
        for record in payload if isinstance(payload, list) else []:
            key = record.get("key") if isinstance(record, dict) else None
            if not key:
                continue
            resolved = zotero_sqlite.resolve_item(
                sqlite_path, key, library_id=library_id
            )
            if resolved:
                results.append(resolved)
        if results:
            return results[:limit]

    collection_id = int(collection["collectionID"]) if collection else None
    return zotero_sqlite.find_items_by_title(
        sqlite_path,
        query,
        library_id=library_id,
        collection_id=collection_id,
        limit=limit,
        exact_title=exact_title,
    )


def get_item(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = session or {}
    resolved = ref if ref is not None else session.get("current_item")
    if resolved is None:
        raise RuntimeError("Item reference required or set it in session first")
    item = zotero_sqlite.resolve_item(
        _require_sqlite(runtime),
        resolved,
        library_id=resolve_library_id(runtime, session.get("current_library")),
    )
    if not item:
        raise RuntimeError(f"Item not found: {resolved}")
    return item


def item_children(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    item = get_item(runtime, ref, session=session)
    return zotero_sqlite.fetch_item_children(_require_sqlite(runtime), item["itemID"])


def item_notes(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    item = get_item(runtime, ref, session=session)
    return zotero_sqlite.fetch_item_notes(_require_sqlite(runtime), item["itemID"])


def item_attachments(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    item = get_item(runtime, ref, session=session)
    attachments = zotero_sqlite.fetch_item_attachments(
        _require_sqlite(runtime), item["itemID"]
    )
    for attachment in attachments:
        attachment["resolvedPath"] = zotero_sqlite.resolve_attachment_real_path(
            attachment, runtime.environment.data_dir
        )
    return attachments


def item_file(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item = get_item(runtime, ref, session=session)
    target = item
    if item["typeName"] != "attachment":
        attachments = item_attachments(runtime, item["itemID"])
        if not attachments:
            raise RuntimeError(f"No attachment file found for item: {item['key']}")
        target = attachments[0]
    resolved_path = zotero_sqlite.resolve_attachment_real_path(
        target, runtime.environment.data_dir
    )
    return {
        "itemID": target["itemID"],
        "key": target["key"],
        "title": target.get("title", ""),
        "contentType": target.get("contentType"),
        "path": target.get("attachmentPath"),
        "resolvedPath": resolved_path,
        "exists": bool(resolved_path and Path(resolved_path).exists()),
    }


def list_searches(
    runtime: RuntimeContext, session: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return zotero_sqlite.fetch_saved_searches(
        _require_sqlite(runtime), library_id=_default_library(runtime, session)
    )


def get_search(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if ref is None:
        raise RuntimeError("Search reference required")
    session = session or {}
    search = zotero_sqlite.resolve_saved_search(
        _require_sqlite(runtime),
        ref,
        library_id=resolve_library_id(runtime, session.get("current_library")),
    )
    if not search:
        raise RuntimeError(f"Saved search not found: {ref}")
    return search
