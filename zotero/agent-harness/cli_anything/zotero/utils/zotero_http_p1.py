# ruff: noqa: F403, F405, E501
from .zotero_http_base import *  # noqa: F403


@dataclass
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: str

    def json(self) -> Any:
        return json.loads(self.body)


def _build_url(port: int, path: str, params: Optional[dict[str, Any]] = None) -> str:
    if not path.startswith("/"):
        path = "/" + path
    url = f"http://127.0.0.1:{port}{path}"
    if params:
        pairs: list[tuple[str, str]] = []
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, (list, tuple)):
                for entry in value:
                    pairs.append((key, str(entry)))
            else:
                pairs.append((key, str(value)))
        if pairs:
            url += "?" + urllib.parse.urlencode(pairs, doseq=True)
    return url


def request(
    port: int,
    path: str,
    *,
    method: str = "GET",
    params: Optional[dict[str, Any]] = None,
    payload: Optional[dict[str, Any]] = None,
    data: bytes | str | None = None,
    headers: Optional[dict[str, str]] = None,
    timeout: int = 5,
) -> HttpResponse:
    request_headers = {"Accept": "*/*"}
    if headers:
        request_headers.update(headers)
    if payload is not None and data is not None:
        raise ValueError("payload and data are mutually exclusive")
    body_data: bytes | None = None
    if payload is not None:
        request_headers.setdefault("Content-Type", "application/json")
        body_data = json.dumps(payload).encode("utf-8")
    elif data is not None:
        body_data = data.encode("utf-8") if isinstance(data, str) else data
        request_headers.setdefault("Content-Type", "text/plain; charset=utf-8")
    req = urllib.request.Request(
        _build_url(port, path, params=params),
        data=body_data,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return HttpResponse(
                response.getcode(), {k: v for k, v in response.headers.items()}, body
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return HttpResponse(exc.code, {k: v for k, v in exc.headers.items()}, body)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"HTTP request failed for {path}: {exc}") from exc


def connector_ping(port: int, timeout: int = 3) -> HttpResponse:
    return request(port, "/connector/ping", timeout=timeout)


def connector_is_available(port: int, timeout: int = 3) -> tuple[bool, str]:
    try:
        response = connector_ping(port, timeout=timeout)
    except RuntimeError as exc:
        return False, str(exc)
    if response.status == 200:
        return True, "connector available"
    return False, f"connector returned HTTP {response.status}"


def get_selected_collection(port: int, timeout: int = 5) -> dict[str, Any]:
    response = request(
        port,
        "/connector/getSelectedCollection",
        method="POST",
        payload={},
        timeout=timeout,
    )
    if response.status != 200:
        raise RuntimeError(
            f"connector/getSelectedCollection returned HTTP {response.status}: {response.body}"
        )
    return response.json()


def connector_import_text(
    port: int, content: str, *, session_id: str | None = None, timeout: int = 300
) -> list[dict[str, Any]]:
    params = {"session": session_id} if session_id else None
    response = request(
        port,
        "/connector/import",
        method="POST",
        params=params,
        data=content,
        timeout=timeout,
    )
    if response.status != 201:
        raise RuntimeError(
            f"connector/import returned HTTP {response.status}: {response.body}"
        )
    parsed = response.json()
    return parsed if isinstance(parsed, list) else [parsed]


def connector_save_items(
    port: int, items: list[dict[str, Any]], *, session_id: str, timeout: int = 120
) -> None:
    response = request(
        port,
        "/connector/saveItems",
        method="POST",
        payload={"sessionID": session_id, "items": items},
        timeout=timeout,
    )
    if response.status != 201:
        raise RuntimeError(
            f"connector/saveItems returned HTTP {response.status}: {response.body}"
        )


def connector_save_attachment(
    port: int,
    *,
    session_id: str,
    parent_item_id: str | int,
    title: str,
    url: str,
    content: bytes,
    timeout: int = 60,
) -> dict[str, Any]:
    response = request(
        port,
        "/connector/saveAttachment",
        method="POST",
        data=content,
        headers={
            "Content-Type": "application/pdf",
            "X-Metadata": json.dumps(
                {
                    "sessionID": session_id,
                    "parentItemID": str(parent_item_id),
                    "title": title,
                    "url": url,
                }
            ),
        },
        timeout=timeout,
    )
    if response.status not in (200, 201):
        raise RuntimeError(
            f"connector/saveAttachment returned HTTP {response.status}: {response.body}"
        )
    return response.json() if response.body else {}
