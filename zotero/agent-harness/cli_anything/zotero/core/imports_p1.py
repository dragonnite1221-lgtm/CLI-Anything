# ruff: noqa: F403, F405, E501
from .imports_base import *  # noqa: F403


def _require_connector(runtime: RuntimeContext) -> None:
    if not runtime.connector_available:
        raise RuntimeError(
            f"Zotero connector is not available: {runtime.connector_message}"
        )


def _read_text_file(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def _read_json_items(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON import file: {path}: {exc}") from exc
    if isinstance(payload, dict):
        payload = payload.get("items")
    if not isinstance(payload, list):
        raise RuntimeError(
            "JSON import expects an array of official Zotero connector item objects"
        )
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f"JSON import item {index} is not an object")
        copied = dict(item)
        copied.setdefault("id", f"cli-anything-zotero-{index}")
        normalized.append(copied)
    return normalized


def _read_json_payload(path: Path, *, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON {label}: {path}: {exc}") from exc


def _default_user_library_target(runtime: RuntimeContext) -> str:
    sqlite_path = runtime.environment.sqlite_path
    if sqlite_path.exists():
        library_id = zotero_sqlite.default_library_id(sqlite_path)
        if library_id is not None:
            return f"L{library_id}"
    return "L1"


def _session_library_id(session: dict[str, Any] | None) -> int | None:
    session = session or {}
    current_library = session.get("current_library")
    if current_library is None:
        return None
    return zotero_sqlite.normalize_library_ref(current_library)


def _resolve_target(
    runtime: RuntimeContext,
    collection_ref: str | None,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = session or {}
    session_library_id = _session_library_id(session)
    if collection_ref:
        if _TREE_VIEW_ID_RE.match(collection_ref):
            kind = "library" if collection_ref.startswith("L") else "collection"
            return {"treeViewID": collection_ref, "source": "explicit", "kind": kind}
        collection = zotero_sqlite.resolve_collection(
            runtime.environment.sqlite_path,
            collection_ref,
            library_id=session_library_id,
        )
        if not collection:
            raise RuntimeError(f"Collection not found: {collection_ref}")
        return {
            "treeViewID": f"C{collection['collectionID']}",
            "source": "explicit",
            "kind": "collection",
            "collectionID": collection["collectionID"],
            "collectionKey": collection["key"],
            "collectionName": collection["collectionName"],
            "libraryID": collection["libraryID"],
        }

    current_collection = session.get("current_collection")
    if current_collection:
        if _TREE_VIEW_ID_RE.match(str(current_collection)):
            kind = (
                "library" if str(current_collection).startswith("L") else "collection"
            )
            return {
                "treeViewID": str(current_collection),
                "source": "session",
                "kind": kind,
            }
        collection = zotero_sqlite.resolve_collection(
            runtime.environment.sqlite_path,
            current_collection,
            library_id=session_library_id,
        )
        if collection:
            return {
                "treeViewID": f"C{collection['collectionID']}",
                "source": "session",
                "kind": "collection",
                "collectionID": collection["collectionID"],
                "collectionKey": collection["key"],
                "collectionName": collection["collectionName"],
                "libraryID": collection["libraryID"],
            }

    if runtime.connector_available:
        selected = zotero_http.get_selected_collection(runtime.environment.port)
        if selected.get("id") is not None:
            return {
                "treeViewID": f"C{selected['id']}",
                "source": "selected",
                "kind": "collection",
                "collectionID": selected["id"],
                "collectionName": selected.get("name"),
                "libraryID": selected.get("libraryID"),
                "libraryName": selected.get("libraryName"),
            }
        return {
            "treeViewID": f"L{selected['libraryID']}",
            "source": "selected",
            "kind": "library",
            "libraryID": selected.get("libraryID"),
            "libraryName": selected.get("libraryName"),
        }

    return {
        "treeViewID": _default_user_library_target(runtime),
        "source": "user_library",
        "kind": "library",
    }


def _normalize_tags(tags: list[str] | tuple[str, ...]) -> list[str]:
    return [tag.strip() for tag in tags if tag and tag.strip()]


def _session_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def _normalize_attachment_int(value: Any, *, name: str, minimum: int) -> int:
    try:
        normalized = int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Attachment `{name}` must be an integer") from exc
    if normalized < minimum:
        comparator = (
            "greater than or equal to" if minimum == 0 else f"at least {minimum}"
        )
        raise RuntimeError(f"Attachment `{name}` must be {comparator}")
    return normalized
