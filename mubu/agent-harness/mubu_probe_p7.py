# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import extract_plain_text  # noqa: E402,E501
from .mubu_probe_p2 import normalized_lookup_key, timestamp_ms_to_iso  # noqa: E402,E501
from .mubu_probe_p4 import iter_nodes  # noqa: E402,E501
from .mubu_probe_p6 import latest_doc_member_context  # noqa: E402,E501
# fmt: on


def resolve_mutation_member_context(
    events: Iterable[dict[str, Any]],
    doc_id: str,
    execute: bool,
) -> dict[str, Any] | None:
    context = latest_doc_member_context(events, doc_id)
    if context is not None:
        return context
    if execute:
        return None
    return {
        "document_id": doc_id,
        "member_id": None,
        "last_seen_at": None,
        "event_type": None,
        "source": "dry_run_placeholder",
        "execute_ready": False,
    }
def plain_text_to_html(value: str) -> str:
    escaped = html.escape(value).replace("\n", "<br>")
    return f"<span>{escaped}</span>"
def maybe_plain_text_to_html(value: str | None) -> str | None:
    if value is None:
        return None
    if value == "":
        return ""
    return plain_text_to_html(value)
def rich_text_to_html(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        raise ValueError(f"unsupported rich text value: {type(value)!r}")

    chunks: list[str] = []
    for segment in value:
        if not isinstance(segment, dict):
            raise ValueError(f"unsupported segment type: {type(segment)!r}")
        if segment.get("type", 1) != 1:
            raise ValueError(f"unsupported segment payload: {segment}")
        text = segment.get("text")
        if not isinstance(text, str):
            raise ValueError(f"segment missing plain text: {segment}")

        classes: list[str] = []
        style = segment.get("style")
        if isinstance(style, dict):
            if style.get("strikethrough"):
                classes.append("strikethrough")
            if style.get("bold"):
                classes.append("bold")
            if style.get("italic"):
                classes.append("italic")
            if style.get("underline"):
                classes.append("underline")

        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        escaped = html.escape(text).replace("\n", "<br>")
        chunks.append(f"<span{class_attr}>{escaped}</span>")
    return "".join(chunks)
def serialize_node(node: dict[str, Any], max_depth: int | None = None, depth: int = 0) -> dict[str, Any]:
    result = {
        "id": node.get("id"),
        "text": extract_plain_text(node.get("text")),
        "note": extract_plain_text(node.get("note")),
        "modified": node.get("modified"),
    }
    if max_depth is None or depth < max_depth:
        result["children"] = [
            serialize_node(child, max_depth=max_depth, depth=depth + 1)
            for child in (node.get("children") or [])
        ]
    return result
def node_path_to_api_path(path: Iterable[Any]) -> list[Any]:
    parts = list(path)
    if not parts or parts[0] != "nodes":
        raise ValueError(f"unsupported node path root: {parts}")
    if "children" in parts:
        return parts

    api_path: list[Any] = ["nodes"]
    for index, part in enumerate(parts[1:]):
        if index == 0:
            api_path.append(part)
        else:
            api_path.extend(["children", part])
    return api_path
def list_document_nodes(
    data: dict[str, Any],
    query: str | None = None,
    max_depth: int | None = None,
) -> list[dict[str, Any]]:
    normalized_query = normalized_lookup_key(query) if query else None
    payload: list[dict[str, Any]] = []

    for path, node in iter_nodes(data.get("nodes", [])):
        depth = len(path) - 1
        if max_depth is not None and depth > max_depth:
            continue

        text = extract_plain_text(node.get("text"))
        note = extract_plain_text(node.get("note"))
        if normalized_query:
            haystack = "\n".join([text, note]).casefold()
            if normalized_query not in haystack:
                continue

        modified = node.get("modified") if isinstance(node.get("modified"), int) else None
        children = node.get("children") or []
        child_count = len(children) if isinstance(children, list) else 0
        payload.append(
            {
                "node_id": node.get("id"),
                "path": ["nodes", *path],
                "api_path": node_path_to_api_path(("nodes", *path)),
                "depth": depth,
                "text": text,
                "note": note,
                "child_count": child_count,
                "modified": modified,
                "modified_at_iso": timestamp_ms_to_iso(modified),
            }
        )

    return payload
