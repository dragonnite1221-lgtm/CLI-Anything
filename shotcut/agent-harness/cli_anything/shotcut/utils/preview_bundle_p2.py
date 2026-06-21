# ruff: noqa: F403, F405, E501
from .preview_bundle_base import *  # noqa: F403

# fmt: off
from .preview_bundle_p1 import _iter_manifests, _load_json, _slug, build_cache_key, bundle_root, find_cached_manifest  # noqa: E402,E501
# fmt: on


def find_latest_manifest(
    software: str,
    recipe: Optional[str] = None,
    bundle_kind: Optional[str] = None,
    project_path: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if root_dir:
        search_root = Path(root_dir).expanduser().resolve() / _slug(software)
    elif project_path:
        search_root = (
            Path(project_path).expanduser().resolve().parent
            / ".cli-anything"
            / "previews"
            / _slug(software)
        )
    else:
        search_root = Path.home() / ".cli-anything" / "previews" / _slug(software)
    if recipe:
        search_root = search_root / _slug(recipe)
    for manifest_path in _iter_manifests(search_root):
        try:
            manifest = _load_json(manifest_path)
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("software") != software:
            continue
        if recipe and manifest.get("recipe") != recipe:
            continue
        if bundle_kind and manifest.get("bundle_kind") != bundle_kind:
            continue
        if manifest.get("status") not in {"ok", "partial"}:
            continue
        manifest["_manifest_path"] = str(manifest_path.resolve())
        manifest["_bundle_dir"] = str(manifest_path.parent.resolve())
        manifest["_summary_path"] = str(
            (
                manifest_path.parent / manifest.get("summary_path", "summary.json")
            ).resolve()
        )
        return manifest
    return None


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
