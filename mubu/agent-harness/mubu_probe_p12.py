# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403


def ambiguous_error_message(kind: str, ref: str, matches: Iterable[dict[str, Any]], path_key: str) -> str:
    options = []
    for item in matches:
        label = item.get(path_key) or item.get("name") or item.get("title") or item.get("doc_id") or item.get("folder_id")
        options.append(str(label))
        if len(options) >= 5:
            break
    suffix = f" matches: {', '.join(options)}" if options else ""
    return f"ambiguous {kind} reference: {ref}.{suffix}"
