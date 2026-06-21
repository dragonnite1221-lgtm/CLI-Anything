# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import extract_plain_text  # noqa: E402,E501
from .mubu_probe_p2 import normalized_lookup_key  # noqa: E402,E501
from .mubu_probe_p3 import build_folder_indexes  # noqa: E402,E501
from .mubu_probe_p4 import dedupe_document_metas_by_logical_path, extract_doc_links, iter_nodes  # noqa: E402,E501
from .mubu_probe_p7 import serialize_node  # noqa: E402,E501
# fmt: on


def show_document(
    documents: Iterable[dict[str, Any]],
    doc_id: str,
    max_depth: int | None = None,
    title_override: str | None = None,
    folder_path: str | None = None,
    doc_path: str | None = None,
) -> dict[str, Any] | None:
    for document in documents:
        if document["doc_id"] != doc_id:
            continue
        return {
            "doc_id": document["doc_id"],
            "title": title_override or document["title"],
            "backup_file": document["backup_file"],
            "modified_at": document["modified_at"],
            "folder_path": folder_path,
            "doc_path": doc_path,
            "view_type": document["data"].get("viewType"),
            "nodes": [
                serialize_node(node, max_depth=max_depth)
                for node in document["data"].get("nodes", [])
            ],
        }
    return None
def resolve_document_reference(
    document_metas: Iterable[dict[str, Any]],
    folders: Iterable[dict[str, Any]],
    doc_ref: str,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    _, folder_paths = build_folder_indexes(folders)
    metas = dedupe_document_metas_by_logical_path(document_metas, folder_paths)

    by_id = [meta for meta in metas if meta.get("doc_id") == doc_ref]
    if len(by_id) == 1:
        return by_id[0], []

    normalized_ref = normalized_lookup_key(doc_ref)

    exact_path = [meta for meta in metas if normalized_lookup_key(meta.get("doc_path")) == normalized_ref]
    if len(exact_path) == 1:
        return exact_path[0], []
    if len(exact_path) > 1:
        return None, exact_path

    suffix_path = [
        meta
        for meta in metas
        if normalized_lookup_key(meta.get("doc_path")).endswith(normalized_ref)
    ]
    if len(suffix_path) == 1:
        return suffix_path[0], []
    if len(suffix_path) > 1:
        return None, suffix_path

    title_matches = [meta for meta in metas if normalized_lookup_key(meta.get("title")) == normalized_ref]
    if len(title_matches) == 1:
        return title_matches[0], []
    if len(title_matches) > 1:
        return None, title_matches

    return None, []
def show_document_by_reference(
    documents: Iterable[dict[str, Any]],
    document_metas: Iterable[dict[str, Any]],
    folders: Iterable[dict[str, Any]],
    doc_ref: str,
    max_depth: int | None = None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    meta, ambiguous = resolve_document_reference(document_metas, folders, doc_ref)
    if meta is None:
        return None, ambiguous
    return (
        show_document(
            documents,
            meta["doc_id"],
            max_depth=max_depth,
            title_override=meta.get("title"),
            folder_path=meta.get("folder_path"),
            doc_path=meta.get("doc_path"),
        ),
        [],
    )
def document_links(
    documents: Iterable[dict[str, Any]],
    doc_id: str,
    title_lookup: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    title_lookup = title_lookup or {}
    for document in documents:
        if document["doc_id"] != doc_id:
            continue
        links: list[dict[str, Any]] = []
        for path, node in iter_nodes(document["data"].get("nodes", [])):
            for field in ("text", "note"):
                for link in extract_doc_links(node.get(field)):
                    links.append(
                        {
                            "source_doc_id": doc_id,
                            "source_doc_title": title_lookup.get(doc_id) or document.get("title"),
                            "source_node_id": node.get("id"),
                            "source_path": list(path),
                            "source_field": field,
                            "source_text": extract_plain_text(node.get("text")),
                            "target_doc_id": link["target_doc_id"],
                            "target_title": title_lookup.get(link["target_doc_id"]),
                            "label": link["label"],
                        }
                    )
        return links
    return []
