# ruff: noqa: F403, F405, E501
from .catalog_base import *  # noqa: F403


def _require_sqlite(runtime: RuntimeContext) -> Path:
    sqlite_path = runtime.environment.sqlite_path
    if not sqlite_path.exists():
        raise FileNotFoundError(f"Zotero SQLite database not found: {sqlite_path}")
    return sqlite_path


def resolve_library_id(
    runtime: RuntimeContext, library_ref: str | int | None
) -> int | None:
    if library_ref is None:
        return None
    sqlite_path = _require_sqlite(runtime)
    library = zotero_sqlite.resolve_library(sqlite_path, library_ref)
    if not library:
        raise RuntimeError(f"Library not found: {library_ref}")
    return int(library["libraryID"])


def _default_library(
    runtime: RuntimeContext, session: dict[str, Any] | None = None
) -> int:
    session = session or {}
    current_library_id = resolve_library_id(runtime, session.get("current_library"))
    if current_library_id is not None:
        return current_library_id
    library_id = zotero_sqlite.default_library_id(_require_sqlite(runtime))
    if library_id is None:
        raise RuntimeError("No Zotero libraries found in the local database")
    return library_id


def local_api_scope(runtime: RuntimeContext, library_id: int) -> str:
    library = zotero_sqlite.resolve_library(_require_sqlite(runtime), library_id)
    if not library:
        raise RuntimeError(f"Library not found: {library_id}")
    if library["type"] == "user":
        return "/api/users/0"
    if library["type"] == "group":
        return f"/api/groups/{int(library['libraryID'])}"
    raise RuntimeError(
        f"Unsupported library type for Zotero Local API: {library['type']}"
    )


def list_libraries(runtime: RuntimeContext) -> list[dict[str, Any]]:
    return zotero_sqlite.fetch_libraries(_require_sqlite(runtime))


def list_collections(
    runtime: RuntimeContext, session: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return zotero_sqlite.fetch_collections(
        _require_sqlite(runtime), library_id=_default_library(runtime, session)
    )


def find_collections(
    runtime: RuntimeContext,
    query: str,
    *,
    limit: int = 20,
    session: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return zotero_sqlite.find_collections(
        _require_sqlite(runtime),
        query,
        library_id=_default_library(runtime, session),
        limit=limit,
    )


def collection_tree(
    runtime: RuntimeContext, session: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return zotero_sqlite.build_collection_tree(
        list_collections(runtime, session=session)
    )


def get_collection(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = session or {}
    resolved = ref if ref is not None else session.get("current_collection")
    if resolved is None:
        raise RuntimeError("Collection reference required or set it in session first")
    collection = zotero_sqlite.resolve_collection(
        _require_sqlite(runtime),
        resolved,
        library_id=resolve_library_id(runtime, session.get("current_library")),
    )
    if not collection:
        raise RuntimeError(f"Collection not found: {resolved}")
    return collection


def collection_items(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    collection = get_collection(runtime, ref, session=session)
    return zotero_sqlite.fetch_items(
        _require_sqlite(runtime),
        library_id=int(collection["libraryID"]),
        collection_id=int(collection["collectionID"]),
    )


def use_selected_collection(runtime: RuntimeContext) -> dict[str, Any]:
    if not runtime.connector_available:
        raise RuntimeError(
            f"Zotero connector is not available: {runtime.connector_message}"
        )
    return zotero_http.get_selected_collection(runtime.environment.port)


def list_items(
    runtime: RuntimeContext,
    session: dict[str, Any] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    return zotero_sqlite.fetch_items(
        _require_sqlite(runtime),
        library_id=_default_library(runtime, session),
        limit=limit,
    )
