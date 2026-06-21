# ruff: noqa: F403, F405, E501
from .imports_base import *  # noqa: F403


def _attachment_result(
    *,
    item_index: int,
    parent_connector_id: Any,
    descriptor: dict[str, Any],
    status: str,
    error: str | None = None,
) -> dict[str, Any]:
    payload = {
        "item_index": item_index,
        "parent_connector_id": parent_connector_id,
        "source_type": descriptor["source_type"],
        "source": descriptor["source"],
        "title": descriptor["title"],
        "status": status,
    }
    if error is not None:
        payload["error"] = error
    return payload


def _attachment_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "planned_count": len(results),
        "created_count": sum(
            1 for result in results if result["status"] == _ATTACHMENT_RESULT_CREATED
        ),
        "failed_count": sum(
            1 for result in results if result["status"] == _ATTACHMENT_RESULT_FAILED
        ),
        "skipped_count": sum(
            1 for result in results if result["status"] == _ATTACHMENT_RESULT_SKIPPED
        ),
    }


def _ensure_pdf_bytes(content: bytes, *, source: str) -> None:
    if not content.startswith(_PDF_MAGIC):
        raise RuntimeError(f"Attachment source is not a PDF: {source}")


def _read_local_pdf(path_text: str) -> tuple[bytes, str]:
    path = Path(path_text).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Attachment file not found: {path}")
    resolved = path.resolve()
    content = resolved.read_bytes()
    _ensure_pdf_bytes(content, source=str(resolved))
    return content, resolved.as_uri()


def _download_remote_pdf(url: str, *, delay_ms: int, timeout: int) -> bytes:
    if delay_ms:
        time.sleep(delay_ms / 1000)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", response.getcode())
            if int(status) != 200:
                raise RuntimeError(f"Attachment download returned HTTP {status}: {url}")
            content = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Attachment download returned HTTP {exc.code}: {url}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Attachment download failed for {url}: {exc.reason}"
        ) from exc
    _ensure_pdf_bytes(content, source=url)
    return content
