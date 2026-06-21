# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import NODE_ID_ALPHABET, extract_plain_text  # noqa: E402,E501
from .mubu_probe_p4 import iter_nodes  # noqa: E402,E501
from .mubu_probe_p7 import plain_text_to_html, rich_text_to_html  # noqa: E402,E501
# fmt: on


def resolve_node_reference_in_data(
    data: dict[str, Any],
    node_id: str | None = None,
    match_text: str | None = None,
    field: str = "text",
) -> tuple[dict[str, Any] | None, tuple[Any, ...] | None, list[dict[str, Any]]]:
    matches: list[dict[str, Any]] = []
    for path, node in iter_nodes(data.get("nodes", [])):
        if node_id and node.get("id") == node_id:
            return node, ("nodes", *path), []
        if match_text and extract_plain_text(node.get(field)) == match_text:
            matches.append({"node": node, "path": ("nodes", *path)})

    if node_id:
        return None, None, []
    if len(matches) == 1:
        return matches[0]["node"], matches[0]["path"], []
    if len(matches) > 1:
        return None, None, matches
    return None, None, []
def resolve_node_at_path(
    data: dict[str, Any],
    path: Iterable[Any],
) -> dict[str, Any] | None:
    parts = list(path)
    if not parts or parts[0] != "nodes":
        raise ValueError(f"unsupported node path root: {parts}")
    if len(parts) < 2:
        raise ValueError(f"node path missing index: {parts}")

    siblings = data.get("nodes")
    if not isinstance(siblings, list):
        return None

    current: dict[str, Any] | None = None
    for part in parts[1:]:
        if not isinstance(part, int):
            raise ValueError(f"unsupported node path segment: {parts}")
        if part < 0 or part >= len(siblings):
            return None
        current = siblings[part]
        children = current.get("children") or []
        siblings = children if isinstance(children, list) else []
    return current
def parent_context_for_path(
    data: dict[str, Any],
    path: Iterable[Any],
) -> tuple[dict[str, Any] | None, tuple[Any, ...] | None, int]:
    parts = tuple(path)
    if not parts or parts[0] != "nodes":
        raise ValueError(f"unsupported node path root: {parts}")
    if len(parts) < 2:
        raise ValueError(f"node path missing index: {parts}")

    index = parts[-1]
    if not isinstance(index, int):
        raise ValueError(f"unsupported node path index: {parts}")
    if len(parts) == 2:
        return None, None, index

    parent_path = parts[:-1]
    parent_node = resolve_node_at_path(data, parent_path)
    if parent_node is None:
        raise ValueError(f"parent node not found for path: {parts}")
    return parent_node, parent_path, index
def generate_node_id(length: int = 10) -> str:
    return "".join(secrets.choice(NODE_ID_ALPHABET) for _ in range(length))
def build_text_update_request(
    doc_id: str,
    member_id: str | None,
    version: int,
    node: dict[str, Any],
    path: Iterable[Any],
    new_text: str,
    field: str = "text",
    modified_ms: int | None = None,
) -> dict[str, Any]:
    modified_ms = modified_ms or int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    if field not in {"text", "note"}:
        raise ValueError(f"unsupported field for text update: {field}")

    current_value = rich_text_to_html(node.get(field))
    updated_node = {
        "id": node.get("id"),
        field: plain_text_to_html(new_text),
        "modified": modified_ms,
        "forceUpdate": True,
    }
    original_node = {
        "id": node.get("id"),
        field: current_value,
        "modified": node.get("modified"),
    }
    return {
        "pathname": "/v3/api/colla/events",
        "method": "POST",
        "data": {
            "memberId": member_id,
            "type": "CHANGE",
            "version": version,
            "documentId": doc_id,
            "events": [
                {
                    "name": "update",
                    "updated": [
                        {
                            "updated": updated_node,
                            "original": original_node,
                            "path": list(path),
                        }
                    ],
                }
            ],
        },
    }
