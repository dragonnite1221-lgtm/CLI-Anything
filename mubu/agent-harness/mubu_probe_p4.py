# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import ANCHOR_RE, DEFAULT_BACKUP_ROOT, HREF_DOC_RE, TOKEN_ATTR_RE, extract_plain_text, load_json  # noqa: E402,E501
from .mubu_probe_p2 import normalized_lookup_key  # noqa: E402,E501
from .mubu_probe_p3 import build_folder_indexes, document_meta_sort_key, enrich_document_meta, resolve_folder_reference  # noqa: E402,E501
# fmt: on


def dedupe_document_metas_by_logical_path(
    document_metas: Iterable[dict[str, Any]],
    folder_paths: dict[str, str],
) -> list[dict[str, Any]]:
    latest_by_path: dict[str, dict[str, Any]] = {}
    for meta in document_metas:
        enriched = enrich_document_meta(meta, folder_paths)
        logical_path = normalized_lookup_key(enriched.get("doc_path"))
        if not logical_path:
            logical_path = f"doc:{normalized_lookup_key(enriched.get('doc_id'))}"
        current = latest_by_path.get(logical_path)
        if current is None or document_meta_sort_key(enriched) >= document_meta_sort_key(current):
            latest_by_path[logical_path] = enriched
    return list(latest_by_path.values())
def folder_documents(
    document_metas: Iterable[dict[str, Any]],
    folders: Iterable[dict[str, Any]],
    folder_ref: str,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None, list[dict[str, Any]]]:
    folder_by_id, folder_paths = build_folder_indexes(folders)
    folder, ambiguous = resolve_folder_reference(folder_by_id.values(), folder_ref)
    if folder is None:
        return [], None, ambiguous

    docs = [
        meta
        for meta in dedupe_document_metas_by_logical_path(document_metas, folder_paths)
        if meta.get("folder_id") == folder.get("folder_id")
    ]
    docs.sort(key=document_meta_sort_key, reverse=True)
    return docs, {**folder, "path": folder_paths.get(folder["folder_id"], "")}, []
def document_meta_by_id(
    document_metas: Iterable[dict[str, Any]],
    folders: Iterable[dict[str, Any]],
    doc_id: str,
) -> dict[str, Any] | None:
    _, folder_paths = build_folder_indexes(folders)
    matches = [
        enrich_document_meta(meta, folder_paths)
        for meta in document_metas
        if meta.get("doc_id") == doc_id
    ]
    if not matches:
        return None
    return max(matches, key=document_meta_sort_key)
def iter_nodes(nodes: Iterable[dict[str, Any]], path: tuple[int, ...] = ()) -> Iterable[tuple[tuple[int, ...], dict[str, Any]]]:
    for index, node in enumerate(nodes):
        current_path = path + (index,)
        yield current_path, node
        children = node.get("children") or []
        if isinstance(children, list):
            yield from iter_nodes(children, current_path)
def infer_title(data: dict[str, Any]) -> str:
    for _, node in iter_nodes(data.get("nodes", [])):
        title = extract_plain_text(node.get("text"))
        if title:
            return title
    return ""
def load_latest_backups(root: Path = DEFAULT_BACKUP_ROOT) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    if not root.exists():
        return documents

    for doc_dir in root.iterdir():
        if not doc_dir.is_dir():
            continue
        files = list(doc_dir.glob("*.json"))
        if not files:
            continue
        latest = max(files, key=lambda candidate: candidate.stat().st_mtime)
        data = load_json(latest)
        documents.append(
            {
                "doc_id": doc_dir.name,
                "backup_file": str(latest),
                "modified_at": latest.stat().st_mtime,
                "title": infer_title(data),
                "data": data,
            }
        )

    documents.sort(key=lambda item: item["modified_at"], reverse=True)
    return documents
def extract_doc_links(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, str):
        return []
    links: list[dict[str, Any]] = []
    for match in ANCHOR_RE.finditer(value):
        attrs = match.group("attrs")
        token_match = TOKEN_ATTR_RE.search(attrs) or HREF_DOC_RE.search(attrs)
        if not token_match:
            continue
        links.append(
            {
                "target_doc_id": token_match.group("token"),
                "label": extract_plain_text(match.group("label")),
            }
        )
    return links
def search_documents(documents: Iterable[dict[str, Any]], query: str, limit: int | None = None) -> list[dict[str, Any]]:
    normalized_query = query.lower()
    hits: list[dict[str, Any]] = []

    for document in documents:
        for path, node in iter_nodes(document["data"].get("nodes", [])):
            text = extract_plain_text(node.get("text"))
            note = extract_plain_text(node.get("note"))
            haystacks = [text.lower(), note.lower()]
            if not any(normalized_query in haystack for haystack in haystacks):
                continue

            hits.append(
                {
                    "doc_id": document["doc_id"],
                    "title": document["title"],
                    "backup_file": document["backup_file"],
                    "path": list(path),
                    "node_id": node.get("id"),
                    "text": text,
                    "note": note,
                }
            )
            if limit is not None and len(hits) >= limit:
                return hits

    return hits
