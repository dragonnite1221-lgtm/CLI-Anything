# ruff: noqa: F403, F405, E501
from .preview_bundle_base import *  # noqa: F403


PROTOCOL_VERSION = "preview-bundle/v1"
TRAJECTORY_PROTOCOL_VERSION = "preview-trajectory/v1"


def _slug(value: str) -> str:
    text = (value or "preview").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "preview"


def _json_dumps(data: Any) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def hash_data(data: Any) -> str:
    return hashlib.sha256(_json_dumps(data).encode("utf-8")).hexdigest()


def fingerprint_data(data: Any) -> str:
    return f"sha256:{hash_data(data)}"


def fingerprint_file(path: str) -> str:
    resolved = os.path.abspath(path)
    stat = os.stat(resolved)
    return fingerprint_data(
        {
            "path": resolved,
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        }
    )


def bundle_root(
    software: str,
    recipe: str,
    project_path: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Path:
    if root_dir:
        base = Path(root_dir).expanduser().resolve()
    elif project_path:
        base = (
            Path(project_path).expanduser().resolve().parent
            / ".cli-anything"
            / "previews"
        )
    else:
        base = Path.home() / ".cli-anything" / "previews"
    return base / _slug(software) / _slug(recipe)


def build_cache_key(
    software: str,
    recipe: str,
    bundle_kind: str,
    source_fingerprint: str,
    options: Optional[Dict[str, Any]] = None,
    harness_version: Optional[str] = None,
    protocol_version: str = PROTOCOL_VERSION,
) -> str:
    return fingerprint_data(
        {
            "protocol_version": protocol_version,
            "software": software,
            "recipe": recipe,
            "bundle_kind": bundle_kind,
            "source_fingerprint": source_fingerprint,
            "options": options or {},
            "harness_version": harness_version or "",
        }
    )


def _iter_manifests(search_root: Path) -> Iterable[Path]:
    if not search_root.exists():
        return []
    return sorted(search_root.rglob("manifest.json"), reverse=True)


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def find_cached_manifest(
    software: str,
    recipe: str,
    bundle_kind: str,
    cache_key: str,
    project_path: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    root = bundle_root(software, recipe, project_path=project_path, root_dir=root_dir)
    for manifest_path in _iter_manifests(root):
        try:
            manifest = _load_json(manifest_path)
        except (OSError, json.JSONDecodeError):
            continue
        if (
            manifest.get("protocol_version") == PROTOCOL_VERSION
            and manifest.get("software") == software
            and manifest.get("recipe") == recipe
            and manifest.get("bundle_kind") == bundle_kind
            and manifest.get("status") in {"ok", "partial"}
            and manifest.get("cache_key") == cache_key
        ):
            manifest["_manifest_path"] = str(manifest_path.resolve())
            manifest["_bundle_dir"] = str(manifest_path.parent.resolve())
            manifest["_summary_path"] = str(
                (
                    manifest_path.parent / manifest.get("summary_path", "summary.json")
                ).resolve()
            )
            return manifest
    return None
