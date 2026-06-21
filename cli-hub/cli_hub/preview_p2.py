# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403
# fmt: off
from .preview_p1 import _TRAJECTORY_CONTAINER_KEYS, _TRAJECTORY_FILENAMES, _TRAJECTORY_PATH_KEYS, _resolve_ref_path  # noqa: E402,E501
# fmt: on


def _iter_trajectory_hints(node: Any, *, _seen: Optional[set[int]] = None) -> Iterable[Tuple[str, Any, str]]:
    if _seen is None:
        _seen = set()
    if not isinstance(node, (dict, list)):
        return
    node_id = id(node)
    if node_id in _seen:
        return
    _seen.add(node_id)
    if isinstance(node, list):
        for item in node:
            yield from _iter_trajectory_hints(item, _seen=_seen)
        return
    for key, value in node.items():
        lower = str(key).lower()
        if lower in _TRAJECTORY_CONTAINER_KEYS:
            if isinstance(value, dict):
                yield ("object", value, lower)
            elif isinstance(value, str):
                yield ("path", value, lower)
        elif lower in _TRAJECTORY_PATH_KEYS and isinstance(value, str):
            yield ("path", value, lower)
        if isinstance(value, (dict, list)):
            yield from _iter_trajectory_hints(value, _seen=_seen)
def _trajectory_candidate_refs(base_dir: Path, *payloads: Dict[str, Any]) -> List[str]:
    refs: List[str] = []
    seen = set()
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for kind, value, _label in _iter_trajectory_hints(payload):
            if kind != "path" or not isinstance(value, str):
                continue
            resolved = _resolve_ref_path(base_dir, value)
            if not resolved.is_file():
                continue
            rel = os.path.relpath(resolved, base_dir)
            if rel not in seen:
                refs.append(rel)
                seen.add(rel)
    for filename in _TRAJECTORY_FILENAMES:
        if filename not in seen:
            refs.append(filename)
            seen.add(filename)
    return refs
def _extract_bundle_payload(item: Dict[str, Any]) -> Dict[str, Any]:
    for key in ("copied_bundle", "bundle", "preview_bundle", "current_bundle", "published_bundle"):
        value = item.get(key)
        if isinstance(value, dict):
            return value
    return item
