# ruff: noqa: F403, F405, E501
from .replay_base import *  # noqa: F403


SUPPORTED_CAPTURE_SUFFIXES = {
    ".ngfx-capture": "graphics_capture",
    ".ngfx-gputrace": "gpu_trace",
}
def _capture_type(path: Path) -> str:
    """Return the supported capture type for a file path."""
    suffix = path.suffix.lower()
    capture_type = SUPPORTED_CAPTURE_SUFFIXES.get(suffix)
    if capture_type is None:
        supported = ", ".join(sorted(SUPPORTED_CAPTURE_SUFFIXES))
        raise ValueError(f"Unsupported Nsight capture file extension '{suffix}'. Expected one of: {supported}.")
    return capture_type
def _write_stdout(path: Path, text: str) -> bool:
    """Write stdout to an artifact file when there is output."""
    if not text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True
def _read_text(path: Path) -> str:
    """Read a generated replay artifact as text, tolerating missing files."""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")
def _load_json_artifact(path: Path) -> tuple[Any | None, str | None]:
    """Load a JSON artifact, returning a parse error instead of raising."""
    text = _read_text(path).strip()
    if not text:
        return None, None
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"{exc.msg} at line {exc.lineno}, column {exc.colno}"
def _top_counts(counter: Counter[str], limit: int = 10) -> list[dict[str, Any]]:
    """Return top counter entries in a stable JSON shape."""
    return [{"name": name, "count": count} for name, count in counter.most_common(limit)]
def _first_value(item: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first non-empty value from a dict."""
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None
def _records_from_json(data: Any, collection_keys: tuple[str, ...]) -> list[dict[str, Any]]:
    """Extract a list of dict records from common metadata JSON shapes."""
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in collection_keys:
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []
def _summarize_metadata(path: Path | None) -> dict[str, Any]:
    """Summarize ngfx-replay --metadata without echoing large environment blocks."""
    if path is None:
        return {"parsed": False}
    data, error = _load_json_artifact(path)
    summary: dict[str, Any] = {"parsed": isinstance(data, dict)}
    if error:
        summary["parse_error"] = error
    if not isinstance(data, dict):
        return summary

    graphics_apis = data.get("graphics_apis")
    if isinstance(graphics_apis, dict):
        api_names = sorted(str(key) for key in graphics_apis)
    elif isinstance(graphics_apis, list):
        api_names = [str(item) for item in graphics_apis]
    else:
        api_names = []

    for key in [
        "nsight_version",
        "nsight_version_build_id",
        "captured_frame",
        "primary_api",
        "primary_gpu",
        "driver_vendor",
        "driver_version",
        "os_information",
        "has_unsupported_operation",
        "non_portable",
    ]:
        if key in data:
            summary[key] = data[key]
    summary["graphics_apis"] = api_names
    summary["process_command_line_present"] = bool(data.get("process_command_line"))
    return summary
