# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import DEFAULT_STORAGE_ROOT  # noqa: E402,E501
from .mubu_probe_p2 import dedupe_latest_records, load_collection_records, normalized_lookup_key, numeric_values, parse_child_refs, parse_revision_generation, timestamp_ms_to_iso  # noqa: E402,E501
# fmt: on


def normalize_folder_record(raw: dict[str, Any]) -> dict[str, Any]:
    updated_at = max(numeric_values(raw.get("|n"), raw.get("|t"), raw.get("|v")), default=None)
    created_at = raw.get("|d") if isinstance(raw.get("|d"), int) else None
    children = parse_child_refs(raw.get("|p"))
    return {
        "folder_id": raw.get("id"),
        "name": raw.get("|o"),
        "parent_id": raw.get("|h") or "0",
        "children": children,
        "created_at": created_at,
        "created_at_iso": timestamp_ms_to_iso(created_at),
        "updated_at": updated_at,
        "updated_at_iso": timestamp_ms_to_iso(updated_at),
        "source": raw.get("|c"),
        "rev": raw.get("_rev"),
    }
def load_folders(storage_root: Path = DEFAULT_STORAGE_ROOT) -> list[dict[str, Any]]:
    records = load_collection_records(
        storage_root,
        "mubu_desktop_app-rxdb-2-folders*/*",
        lambda obj: "|o" in obj and isinstance(obj.get("id"), str),
    )
    return [normalize_folder_record(record) for record in dedupe_latest_records(records, timestamp_fields=["|n", "|t", "|v"])]
def normalize_document_meta_record(raw: dict[str, Any]) -> dict[str, Any]:
    created_at = raw.get("|e") if isinstance(raw.get("|e"), int) else None
    updated_at = max(numeric_values(raw.get("|m"), raw.get("|B"), raw.get("|z"), raw.get("|e")), default=None)
    return {
        "doc_id": raw.get("id"),
        "folder_id": raw.get("|h") or "0",
        "title": raw.get("|n"),
        "created_at": created_at,
        "created_at_iso": timestamp_ms_to_iso(created_at),
        "updated_at": updated_at,
        "updated_at_iso": timestamp_ms_to_iso(updated_at),
        "word_count": raw.get("|j") if isinstance(raw.get("|j"), int) else None,
        "source": raw.get("|d"),
        "rev": raw.get("_rev"),
    }
def load_document_metas(storage_root: Path = DEFAULT_STORAGE_ROOT) -> list[dict[str, Any]]:
    records = load_collection_records(
        storage_root,
        "mubu_desktop_app-rxdb-1-document_meta*/*",
        lambda obj: "|n" in obj and "|h" in obj and isinstance(obj.get("id"), str),
    )
    return [
        normalize_document_meta_record(record)
        for record in dedupe_latest_records(records, timestamp_fields=["|m", "|B", "|z", "|e"])
    ]
def build_folder_indexes(folders: Iterable[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    by_id = {folder["folder_id"]: folder for folder in folders if folder.get("folder_id")}
    path_cache: dict[str, str] = {}

    def build_path(folder_id: str | None) -> str:
        if not folder_id or folder_id == "0":
            return ""
        if folder_id in path_cache:
            return path_cache[folder_id]
        folder = by_id.get(folder_id)
        if not folder:
            return ""
        parent_path = build_path(folder.get("parent_id"))
        current = folder.get("name") or folder_id
        path_cache[folder_id] = f"{parent_path}/{current}" if parent_path else current
        return path_cache[folder_id]

    for folder_id in by_id:
        build_path(folder_id)

    return by_id, path_cache
def resolve_folder_reference(
    folders: Iterable[dict[str, Any]],
    folder_ref: str,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    folder_by_id, folder_paths = build_folder_indexes(folders)
    if folder_ref in folder_by_id:
        return folder_by_id[folder_ref], []

    normalized_ref = normalized_lookup_key(folder_ref)
    exact = [folder for folder in folder_by_id.values() if normalized_lookup_key(folder_paths.get(folder["folder_id"], "")) == normalized_ref]
    if len(exact) == 1:
        return exact[0], []
    if len(exact) > 1:
        return None, exact

    suffix = [
        folder
        for folder in folder_by_id.values()
        if normalized_lookup_key(folder_paths.get(folder["folder_id"], "")).endswith(normalized_ref)
    ]
    if len(suffix) == 1:
        return suffix[0], []
    if len(suffix) > 1:
        return None, suffix

    name_matches = [folder for folder in folder_by_id.values() if normalized_lookup_key(folder.get("name")) == normalized_ref]
    if len(name_matches) == 1:
        return name_matches[0], []
    if len(name_matches) > 1:
        return None, name_matches

    return None, []
def enrich_document_meta(
    meta: dict[str, Any],
    folder_paths: dict[str, str],
) -> dict[str, Any]:
    folder_path = folder_paths.get(meta.get("folder_id", ""), "")
    doc_path = folder_path
    if meta.get("title"):
        doc_path = f"{folder_path}/{meta['title']}" if folder_path else meta["title"]
    return {
        **meta,
        "folder_path": folder_path,
        "doc_path": doc_path,
    }
def document_meta_sort_key(meta: dict[str, Any]) -> tuple[int, int, str]:
    return (
        max(
            numeric_values(
                meta.get("updated_at"),
                meta.get("created_at"),
                meta.get("modified_at"),
            ),
            default=0,
        ),
        parse_revision_generation(meta.get("_rev") or meta.get("rev")),
        str(meta.get("doc_id") or ""),
    )
