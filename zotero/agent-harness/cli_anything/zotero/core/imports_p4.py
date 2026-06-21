# ruff: noqa: F403, F405, E501
from .imports_base import *  # noqa: F403

# fmt: off
from .imports_p2 import _item_title, _normalize_url_for_dedupe  # noqa: E402,E501
from .imports_p3 import _attachment_result, _attachment_summary, _download_remote_pdf, _read_local_pdf  # noqa: E402,E501
# fmt: on


def _perform_attachment_upload(
    runtime: RuntimeContext,
    *,
    session_id: str,
    connector_items: list[dict[str, Any]],
    plans: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    seen_by_item: dict[str, dict[str, set[str]]] = {}
    for plan in plans:
        item_index = int(plan["index"])
        attachments = list(plan.get("attachments") or [])
        imported_item = (
            connector_items[item_index]
            if 0 <= item_index < len(connector_items)
            else None
        )
        expected_title = plan.get("expected_title")
        if imported_item is None:
            message = f"Import returned no item at index {item_index}"
            results.extend(
                _attachment_result(
                    item_index=item_index,
                    parent_connector_id=None,
                    descriptor=descriptor,
                    status=_ATTACHMENT_RESULT_FAILED,
                    error=message,
                )
                for descriptor in attachments
            )
            continue
        imported_title = _item_title(imported_item)
        if expected_title is not None and imported_title != expected_title:
            message = (
                f"Imported item title mismatch at index {item_index}: "
                f"expected {expected_title!r}, got {imported_title!r}"
            )
            results.extend(
                _attachment_result(
                    item_index=item_index,
                    parent_connector_id=imported_item.get("id"),
                    descriptor=descriptor,
                    status=_ATTACHMENT_RESULT_FAILED,
                    error=message,
                )
                for descriptor in attachments
            )
            continue
        parent_connector_id = imported_item.get("id")
        if not parent_connector_id:
            message = (
                f"Imported item at index {item_index} did not include a connector id"
            )
            results.extend(
                _attachment_result(
                    item_index=item_index,
                    parent_connector_id=None,
                    descriptor=descriptor,
                    status=_ATTACHMENT_RESULT_FAILED,
                    error=message,
                )
                for descriptor in attachments
            )
            continue

        dedupe_state = seen_by_item.setdefault(
            str(parent_connector_id),
            {"paths": set(), "urls": set(), "hashes": set()},
        )
        for descriptor in attachments:
            try:
                if descriptor["source_type"] == "file":
                    canonical_path = str(
                        Path(descriptor["source"]).expanduser().resolve()
                    )
                    if canonical_path in dedupe_state["paths"]:
                        results.append(
                            _attachment_result(
                                item_index=item_index,
                                parent_connector_id=parent_connector_id,
                                descriptor=descriptor,
                                status=_ATTACHMENT_RESULT_SKIPPED,
                            )
                        )
                        continue
                    content, metadata_url = _read_local_pdf(descriptor["source"])
                else:
                    normalized_url = _normalize_url_for_dedupe(descriptor["source"])
                    if normalized_url in dedupe_state["urls"]:
                        results.append(
                            _attachment_result(
                                item_index=item_index,
                                parent_connector_id=parent_connector_id,
                                descriptor=descriptor,
                                status=_ATTACHMENT_RESULT_SKIPPED,
                            )
                        )
                        continue
                    content = _download_remote_pdf(
                        descriptor["source"],
                        delay_ms=int(descriptor["delay_ms"]),
                        timeout=int(descriptor["timeout"]),
                    )
                    metadata_url = descriptor["source"]

                content_hash = hashlib.sha256(content).hexdigest()
                if content_hash in dedupe_state["hashes"]:
                    results.append(
                        _attachment_result(
                            item_index=item_index,
                            parent_connector_id=parent_connector_id,
                            descriptor=descriptor,
                            status=_ATTACHMENT_RESULT_SKIPPED,
                        )
                    )
                    continue

                zotero_http.connector_save_attachment(
                    runtime.environment.port,
                    session_id=session_id,
                    parent_item_id=parent_connector_id,
                    title=descriptor["title"],
                    url=metadata_url,
                    content=content,
                    timeout=int(descriptor["timeout"]),
                )
                dedupe_state["hashes"].add(content_hash)
                if descriptor["source_type"] == "file":
                    dedupe_state["paths"].add(canonical_path)
                else:
                    dedupe_state["urls"].add(normalized_url)
                results.append(
                    _attachment_result(
                        item_index=item_index,
                        parent_connector_id=parent_connector_id,
                        descriptor=descriptor,
                        status=_ATTACHMENT_RESULT_CREATED,
                    )
                )
            except Exception as exc:
                results.append(
                    _attachment_result(
                        item_index=item_index,
                        parent_connector_id=parent_connector_id,
                        descriptor=descriptor,
                        status=_ATTACHMENT_RESULT_FAILED,
                        error=str(exc),
                    )
                )
    return _attachment_summary(results), results
