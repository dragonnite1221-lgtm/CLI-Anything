# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def list_recipes() -> List[Dict[str, Any]]:
    """Return available preview recipes."""
    return [
        {
            "name": name,
            "description": config["description"],
            "bundle_kind": "capture",
            "artifacts": ["hero", "gallery"],
            "presets": [config["primary_preset"], config["secondary_preset"]],
        }
        for name, config in RECIPES.items()
    ]


def _project_fingerprint(session: Session) -> str:
    project = session.get_project()
    payload: Dict[str, Any] = {
        "project": project,
        "project_path": os.path.abspath(session.project_path)
        if session.project_path
        else "",
    }
    if not session.project_path:
        metadata = project.get("metadata") or {}
        payload["project_created"] = metadata.get("created")
    return fingerprint_data(payload)


def _slug(value: str) -> str:
    text = (value or "preview").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "preview"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_poll_ms(value: Optional[int]) -> int:
    try:
        numeric = int(value or DEFAULT_SOURCE_POLL_MS)
    except (TypeError, ValueError):
        numeric = DEFAULT_SOURCE_POLL_MS
    return max(MIN_SOURCE_POLL_MS, numeric)


def _project_file_fingerprint(project_path: Optional[str]) -> Optional[str]:
    if not project_path:
        return None
    resolved = os.path.abspath(project_path)
    if not os.path.isfile(resolved):
        return None
    return fingerprint_file(resolved)


def _preview_base_dir(
    project_path: Optional[str] = None, root_dir: Optional[str] = None
) -> Path:
    if root_dir:
        return Path(root_dir).expanduser().resolve() / "blender"
    if project_path:
        return (
            Path(project_path).expanduser().resolve().parent
            / ".cli-anything"
            / "previews"
            / "blender"
        )
    return Path.home() / ".cli-anything" / "previews" / "blender"


def _live_session_name(session: Session, recipe: str) -> str:
    project = session.get_project()
    project_name = (
        Path(session.project_path).stem
        if session.project_path
        else project.get("name", "untitled")
    )
    if session.project_path:
        fingerprint_source: Dict[str, Any] = {
            "project_path": os.path.abspath(session.project_path),
            "recipe": recipe,
        }
    else:
        metadata = project.get("metadata") or {}
        fingerprint_source = {
            "project_name": project_name,
            "project_created": metadata.get("created"),
            "recipe": recipe,
        }
    suffix = fingerprint_data(fingerprint_source).split(":", 1)[-1][:8]
    return f"{_slug(project_name)}-{suffix}-{_slug(recipe)}"


def _live_session_dir(
    session: Session, recipe: str, root_dir: Optional[str] = None
) -> Path:
    return (
        _preview_base_dir(session.project_path, root_dir=root_dir)
        / "live"
        / _live_session_name(session, recipe)
    )


def _read_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)
        fh.write("\n")
    return path


def _merge_nested_dict(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge_nested_dict(base[key], value)
        else:
            base[key] = value
    return base


def _pid_is_running(pid: Any) -> bool:
    try:
        numeric = int(pid)
    except (TypeError, ValueError):
        return False
    if numeric <= 0:
        return False
    try:
        os.kill(numeric, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _terminate_pid(pid: Any) -> bool:
    try:
        numeric = int(pid)
    except (TypeError, ValueError):
        return False
    if numeric <= 0:
        return False
    try:
        os.kill(numeric, signal.SIGTERM)
        return True
    except ProcessLookupError:
        return False


def _with_live_refs(session_dir: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["_session_dir"] = str(session_dir.resolve())
    payload["_session_path"] = str((session_dir / "session.json").resolve())
    trajectory_path = live_trajectory_path(session_dir)
    if trajectory_path.is_file():
        payload["_trajectory_path"] = str(trajectory_path.resolve())
    return payload
