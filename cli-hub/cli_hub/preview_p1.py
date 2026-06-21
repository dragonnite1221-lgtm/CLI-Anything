# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _read_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
def resolve_bundle_ref(bundle_ref: str) -> Tuple[Path, Path]:
    ref = Path(bundle_ref).expanduser().resolve()
    if ref.is_dir():
        manifest = ref / "manifest.json"
        if not manifest.is_file():
            raise FileNotFoundError(f"manifest.json not found in bundle directory: {ref}")
        return ref, manifest
    if ref.is_file():
        if ref.name != "manifest.json":
            raise ValueError("Bundle ref must be a bundle directory or a manifest.json path")
        return ref.parent, ref
    raise FileNotFoundError(f"Bundle ref not found: {bundle_ref}")
def resolve_session_ref(session_ref: str) -> Tuple[Path, Path]:
    ref = Path(session_ref).expanduser().resolve()
    if ref.is_dir():
        session_path = ref / "session.json"
        if not session_path.is_file():
            raise FileNotFoundError(f"session.json not found in live session directory: {ref}")
        return ref, session_path
    if ref.is_file():
        if ref.name != "session.json":
            raise ValueError("Session ref must be a live session directory or a session.json path")
        return ref.parent, ref
    raise FileNotFoundError(f"Session ref not found: {session_ref}")
def is_live_session_ref(preview_ref: str) -> bool:
    ref = Path(preview_ref).expanduser().resolve()
    if ref.is_dir():
        return (ref / "session.json").is_file()
    return ref.is_file() and ref.name == "session.json"
def load_bundle(bundle_ref: str) -> Tuple[Path, Dict[str, Any], Dict[str, Any]]:
    bundle_dir, manifest_path = resolve_bundle_ref(bundle_ref)
    manifest = _read_json(manifest_path)
    summary_rel = manifest.get("summary_path", "summary.json")
    summary_path = (bundle_dir / summary_rel).resolve()
    summary = _read_json(summary_path) if summary_path.is_file() else {}
    return bundle_dir, manifest, summary
def load_session(session_ref: str) -> Tuple[Path, Dict[str, Any]]:
    session_dir, session_path = resolve_session_ref(session_ref)
    return session_dir, _read_json(session_path)
def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    return f"{size / (1024 * 1024 * 1024):.1f} GB"
_TRAJECTORY_FILENAMES = ("trajectory.json", "timeline.json")
_TRAJECTORY_CONTAINER_KEYS = {"trajectory", "timeline"}
_TRAJECTORY_PATH_KEYS = {
    "trajectory_path",
    "timeline_path",
    "trajectory_file",
    "timeline_file",
    "trajectory_ref",
    "timeline_ref",
}
def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None
def _stringify_command(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    if isinstance(value, (list, tuple)):
        text = " ".join(str(part) for part in value if part is not None)
        return text.strip() or None
    if isinstance(value, dict):
        for key in ("display", "display_cmd", "command", "raw", "argv"):
            if key in value:
                return _stringify_command(value[key])
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)
def _script_json(value: Any) -> str:
    """Serialize JSON safely for embedding inside a script tag."""
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
def _normalize_index(value: Any, fallback: int) -> int:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
    return fallback
def _resolve_ref_path(base_dir: Path, path_ref: str) -> Path:
    ref = Path(path_ref).expanduser()
    if not ref.is_absolute():
        ref = (base_dir / ref).resolve()
    else:
        ref = ref.resolve()
    return ref
