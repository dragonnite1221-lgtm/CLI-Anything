# ruff: noqa: F403, F405, E501
from .preview_bundle_base import *  # noqa: F403

# fmt: off
from .preview_bundle_p1 import _load_json, _slug, build_cache_key, bundle_root, find_cached_manifest  # noqa: E402,E501
# fmt: on


def prepare_bundle(
    software: str,
    recipe: str,
    bundle_kind: str,
    source_fingerprint: str,
    options: Optional[Dict[str, Any]] = None,
    harness_version: Optional[str] = None,
    project_path: Optional[str] = None,
    root_dir: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    cache_key = build_cache_key(
        software=software,
        recipe=recipe,
        bundle_kind=bundle_kind,
        source_fingerprint=source_fingerprint,
        options=options or {},
        harness_version=harness_version,
    )
    if not force:
        cached = find_cached_manifest(
            software=software,
            recipe=recipe,
            bundle_kind=bundle_kind,
            cache_key=cache_key,
            project_path=project_path,
            root_dir=root_dir,
        )
        if cached:
            return {
                "cached": True,
                "cache_key": cache_key,
                "bundle_id": cached.get("bundle_id"),
                "bundle_dir": cached["_bundle_dir"],
                "manifest_path": cached["_manifest_path"],
                "summary_path": os.path.join(
                    cached["_bundle_dir"], cached.get("summary_path", "summary.json")
                ),
                "manifest": cached,
            }

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_id = f"{now}_{cache_key.split(':', 1)[-1][:8]}_{_slug(recipe)}"
    out_dir = (
        bundle_root(software, recipe, project_path=project_path, root_dir=root_dir)
        / bundle_id
    )
    artifacts_dir = out_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=False)
    return {
        "cached": False,
        "cache_key": cache_key,
        "bundle_id": bundle_id,
        "bundle_dir": str(out_dir.resolve()),
        "artifacts_dir": str(artifacts_dir.resolve()),
        "manifest_path": str((out_dir / "manifest.json").resolve()),
        "summary_path": str((out_dir / "summary.json").resolve()),
    }


def artifact_record(
    bundle_dir: str,
    path: str,
    artifact_id: str,
    role: str,
    kind: str,
    label: str,
    media_type: Optional[str] = None,
    **extra: Any,
) -> Dict[str, Any]:
    bundle_path = Path(bundle_dir).resolve()
    file_path = Path(path).resolve()
    rel_path = file_path.relative_to(bundle_path).as_posix()
    record: Dict[str, Any] = {
        "artifact_id": artifact_id,
        "role": role,
        "kind": kind,
        "label": label,
        "media_type": media_type
        or mimetypes.guess_type(str(file_path))[0]
        or "application/octet-stream",
        "path": rel_path,
    }
    if file_path.exists():
        record["bytes"] = file_path.stat().st_size
    record.update({k: v for k, v in extra.items() if v is not None})
    return record


def write_json(path: str, data: Any) -> str:
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False, default=str)
        fh.write("\n")
    return str(output_path)


def finalize_bundle(
    bundle_dir: str,
    bundle_id: str,
    bundle_kind: str,
    software: str,
    recipe: str,
    source: Dict[str, Any],
    artifacts: list[Dict[str, Any]],
    summary: Dict[str, Any],
    cache_key: str,
    generator: Dict[str, Any],
    status: str = "ok",
    warnings: Optional[list[str]] = None,
    context: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    labels: Optional[list[str]] = None,
    source_bundles: Optional[list[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    bundle_path = Path(bundle_dir).resolve()
    summary_rel = "summary.json"
    summary_path = write_json(str(bundle_path / summary_rel), summary)
    manifest = {
        "protocol_version": PROTOCOL_VERSION,
        "bundle_id": bundle_id,
        "bundle_kind": bundle_kind,
        "software": software,
        "recipe": recipe,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cache_key": cache_key,
        "generator": generator,
        "source": source,
        "summary_path": summary_rel,
        "artifacts": artifacts,
    }
    if warnings:
        manifest["warnings"] = warnings
    if context:
        manifest["context"] = context
    if metrics:
        manifest["metrics"] = metrics
    if labels:
        manifest["labels"] = labels
    if source_bundles:
        manifest["source_bundles"] = source_bundles
    manifest_path = write_json(str(bundle_path / "manifest.json"), manifest)
    manifest["_manifest_path"] = manifest_path
    manifest["_bundle_dir"] = str(bundle_path)
    manifest["_summary_path"] = summary_path
    return manifest


def _clean_none_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def live_trajectory_path(session_dir: str | Path) -> Path:
    return Path(session_dir).expanduser().resolve() / "trajectory.json"


def load_live_trajectory(session_dir: str | Path) -> Dict[str, Any]:
    trajectory_path = live_trajectory_path(session_dir)
    if not trajectory_path.is_file():
        return {}
    return _load_json(trajectory_path)
