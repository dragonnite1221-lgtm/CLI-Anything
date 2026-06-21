# ruff: noqa: F403, F405, E501
from .zotero_http_base import *  # noqa: F403

# fmt: off
from .zotero_http_p1 import HttpResponse, request  # noqa: E402,E501
# fmt: on


def connector_update_session(
    port: int,
    *,
    session_id: str,
    target: str,
    tags: list[str] | tuple[str, ...] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    response = request(
        port,
        "/connector/updateSession",
        method="POST",
        payload={
            "sessionID": session_id,
            "target": target,
            "tags": ", ".join(tag for tag in (tags or []) if str(tag).strip()),
        },
        timeout=timeout,
    )
    if response.status != 200:
        raise RuntimeError(
            f"connector/updateSession returned HTTP {response.status}: {response.body}"
        )
    return response.json() if response.body else {}


def local_api_root(port: int, timeout: int = 3) -> HttpResponse:
    return request(
        port,
        "/api/",
        headers={"Zotero-API-Version": LOCAL_API_VERSION},
        timeout=timeout,
    )


def local_api_is_available(port: int, timeout: int = 3) -> tuple[bool, str]:
    try:
        response = local_api_root(port, timeout=timeout)
    except RuntimeError as exc:
        return False, str(exc)
    if response.status == 200:
        return True, "local API available"
    if response.status == 403:
        return False, "local API disabled"
    return False, f"local API returned HTTP {response.status}"


def wait_for_endpoint(
    port: int,
    path: str,
    *,
    timeout: int = 30,
    poll_interval: float = 0.5,
    headers: Optional[dict[str, str]] = None,
    ready_statuses: tuple[int, ...] = (200,),
) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = request(port, path, headers=headers, timeout=3)
            if response.status in ready_statuses:
                return True
        except RuntimeError:
            pass
        time.sleep(poll_interval)
    return False


def local_api_get_json(
    port: int, path: str, params: Optional[dict[str, Any]] = None, timeout: int = 10
) -> Any:
    response = request(
        port,
        path,
        params=params,
        headers={"Zotero-API-Version": LOCAL_API_VERSION, "Accept": "application/json"},
        timeout=timeout,
    )
    if response.status != 200:
        raise RuntimeError(
            f"Local API returned HTTP {response.status} for {path}: {response.body}"
        )
    return response.json()


def local_api_get_text(
    port: int, path: str, params: Optional[dict[str, Any]] = None, timeout: int = 15
) -> str:
    response = request(
        port,
        path,
        params=params,
        headers={"Zotero-API-Version": LOCAL_API_VERSION},
        timeout=timeout,
    )
    if response.status != 200:
        raise RuntimeError(
            f"Local API returned HTTP {response.status} for {path}: {response.body}"
        )
    return response.body
