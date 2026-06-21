# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def latest(
    *,
    project_path: Optional[str] = None,
    recipe: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Return the latest preview bundle manifest for Shotcut."""
    manifest = find_latest_manifest(
        software="shotcut",
        recipe=recipe,
        bundle_kind="capture",
        project_path=project_path,
        root_dir=root_dir,
    )
    if manifest is None:
        raise FileNotFoundError("No Shotcut preview bundle found")
    return manifest


def _slug(value: str) -> str:
    text = (value or "preview").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "preview"


def _preview_base_dir(
    project_path: Optional[str] = None, root_dir: Optional[str] = None
) -> Path:
    if root_dir:
        return Path(root_dir).expanduser().resolve() / "shotcut"
    if project_path:
        return (
            Path(project_path).expanduser().resolve().parent
            / ".cli-anything"
            / "previews"
            / "shotcut"
        )
    return Path.home() / ".cli-anything" / "previews" / "shotcut"


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


def _live_session_name(session: Session, recipe: str) -> str:
    project_name = (
        Path(session.project_path).stem
        if session.project_path
        else session.session_id or "untitled"
    )
    fingerprint_source = {
        "project_path": os.path.abspath(session.project_path)
        if session.project_path
        else "",
        "recipe": recipe,
    }
    if not session.project_path:
        fingerprint_source["session_id"] = session.session_id
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


def _load_existing_live_session(session_dir: Path) -> Dict[str, Any]:
    session_path = session_dir / "session.json"
    if session_path.is_file():
        return _read_json(session_path)
    return {}


def _write_live_session_updates(
    session_dir: Path, updates: Dict[str, Any]
) -> Dict[str, Any]:
    payload = _load_existing_live_session(session_dir)
    if not payload:
        raise FileNotFoundError(f"Live preview session not found: {session_dir}")
    _merge_nested_dict(payload, updates)
    payload["updated_at"] = updates.get("updated_at", _now_iso())
    _write_json(session_dir / "session.json", payload)
    return _with_live_refs(session_dir, payload)


def _update_current_symlink(session_dir: Path, bundle_dir: str) -> Path:
    current_link = session_dir / "current"
    if current_link.is_symlink() or current_link.exists():
        if current_link.is_dir() and not current_link.is_symlink():
            raise RuntimeError(
                f"Live preview current path is unexpectedly a directory: {current_link}"
            )
        current_link.unlink()
    target = os.path.relpath(Path(bundle_dir).resolve(), session_dir)
    os.symlink(target, current_link, target_is_directory=True)
    return current_link


def _history_item(bundle_manifest: Dict[str, Any]) -> Dict[str, Any]:
    return build_live_history_item(bundle_manifest)
