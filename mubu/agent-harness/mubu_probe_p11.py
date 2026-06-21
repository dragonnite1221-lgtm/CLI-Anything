# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403
# fmt: off
from .mubu_probe_p1 import DEFAULT_API_HOST  # noqa: E402,E501
from .mubu_probe_p2 import post_json  # noqa: E402,E501
from .mubu_probe_p6 import build_api_headers  # noqa: E402,E501
from .mubu_probe_p9 import build_text_update_request  # noqa: E402,E501
from .mubu_probe_p10 import build_create_child_request, build_delete_node_request  # noqa: E402,E501
# fmt: on


def perform_text_update(
    user: dict[str, Any],
    doc_id: str,
    member_id: str | None,
    version: int,
    node: dict[str, Any],
    path: Iterable[Any],
    new_text: str,
    field: str = "text",
    execute: bool = False,
    api_host: str = DEFAULT_API_HOST,
) -> dict[str, Any]:
    request_payload = build_text_update_request(
        doc_id=doc_id,
        member_id=member_id,
        version=version,
        node=node,
        path=path,
        new_text=new_text,
        field=field,
    )
    if not execute:
        return {
            "execute": False,
            "request": request_payload,
        }

    response = post_json(
        f"{api_host}{request_payload['pathname']}",
        request_payload["data"],
        build_api_headers(user),
    )
    return {
        "execute": True,
        "request": request_payload,
        "response": response,
    }
def perform_create_child(
    user: dict[str, Any],
    doc_id: str,
    member_id: str | None,
    version: int,
    parent_node: dict[str, Any],
    parent_path: Iterable[Any],
    text: str,
    note: str | None = None,
    index: int | None = None,
    execute: bool = False,
    api_host: str = DEFAULT_API_HOST,
) -> dict[str, Any]:
    request_payload = build_create_child_request(
        doc_id=doc_id,
        member_id=member_id,
        version=version,
        parent_node=parent_node,
        parent_path=parent_path,
        text=text,
        note=note,
        index=index,
    )
    if not execute:
        return {
            "execute": False,
            "request": request_payload,
        }

    response = post_json(
        f"{api_host}{request_payload['pathname']}",
        request_payload["data"],
        build_api_headers(user),
    )
    return {
        "execute": True,
        "request": request_payload,
        "response": response,
    }
def perform_delete_node(
    user: dict[str, Any],
    doc_id: str,
    member_id: str | None,
    version: int,
    node: dict[str, Any],
    path: Iterable[Any],
    parent_node: dict[str, Any] | None = None,
    execute: bool = False,
    api_host: str = DEFAULT_API_HOST,
) -> dict[str, Any]:
    request_payload = build_delete_node_request(
        doc_id=doc_id,
        member_id=member_id,
        version=version,
        node=node,
        path=path,
        parent_node=parent_node,
    )
    if not execute:
        return {
            "execute": False,
            "request": request_payload,
        }

    response = post_json(
        f"{api_host}{request_payload['pathname']}",
        request_payload["data"],
        build_api_headers(user),
    )
    return {
        "execute": True,
        "request": request_payload,
        "response": response,
    }
def dump_output(data: Any, as_json: bool) -> None:
    if as_json:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return

    if isinstance(data, list):
        for item in data:
            print(json.dumps(item, ensure_ascii=False))
        return

    print(json.dumps(data, ensure_ascii=False, indent=2))
