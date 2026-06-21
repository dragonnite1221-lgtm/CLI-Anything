# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p7 import maybe_plain_text_to_html, node_path_to_api_path  # noqa: E402,E501
from .mubu_probe_p9 import generate_node_id  # noqa: E402,E501
# fmt: on


def build_create_child_request(
    doc_id: str,
    member_id: str | None,
    version: int,
    parent_node: dict[str, Any],
    parent_path: Iterable[Any],
    text: str,
    note: str | None = None,
    child_id: str | None = None,
    index: int | None = None,
    modified_ms: int | None = None,
) -> dict[str, Any]:
    modified_ms = modified_ms or int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    child_id = child_id or generate_node_id()

    children = parent_node.get("children") or []
    if not isinstance(children, list):
        children = []

    if index is None:
        index = len(children)
    if index < 0 or index > len(children):
        raise ValueError(f"child index out of range: {index}")

    node_payload = {
        "id": child_id,
        "taskStatus": 0,
        "text": maybe_plain_text_to_html(text) or "",
        "modified": modified_ms,
        "children": [],
    }
    note_html = maybe_plain_text_to_html(note)
    if note_html is not None:
        node_payload["note"] = note_html
    if text or (note is not None and note != ""):
        node_payload["forceUpdate"] = True

    create_path = node_path_to_api_path(parent_path) + ["children", index]
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
                    "name": "create",
                    "created": [
                        {
                            "index": index,
                            "parentId": parent_node.get("id"),
                            "node": node_payload,
                            "path": create_path,
                        }
                    ],
                }
            ],
        },
    }
def build_delete_node_request(
    doc_id: str,
    member_id: str | None,
    version: int,
    node: dict[str, Any],
    path: Iterable[Any],
    parent_node: dict[str, Any] | None = None,
) -> dict[str, Any]:
    deleted_node = copy.deepcopy(node)
    children = deleted_node.get("children")
    if not isinstance(children, list):
        deleted_node["children"] = []

    raw_path = tuple(path)
    if len(raw_path) < 2:
        raise ValueError(f"node path missing index: {raw_path}")
    index = raw_path[-1]
    if not isinstance(index, int):
        raise ValueError(f"unsupported node path index: {raw_path}")

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
                    "name": "delete",
                    "deleted": [
                        {
                            "parentId": parent_node.get("id") if parent_node else None,
                            "index": index,
                            "node": deleted_node,
                            "path": node_path_to_api_path(raw_path),
                        }
                    ],
                }
            ],
        },
    }
