# ruff: noqa: F403, F405, E501
from .unrealinsights_backend_base import *  # noqa: F403


def _normalize_path(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())


def _extract_engine_version_hint(path: Path) -> str | None:
    for parent in path.parents:
        if parent.name.startswith("UE_"):
            return parent.name.removeprefix("UE_")
    return None


def _engine_sort_key(path: Path) -> tuple[int, ...]:
    match = re.findall(r"\d+", path.name)
    if not match:
        return (0,)
    return tuple(int(part) for part in match)


def _default_search_roots() -> list[Path]:
    roots: dict[str, Path] = {}

    for env_key in ("ProgramW6432", "ProgramFiles"):
        value = os.environ.get(env_key)
        if value:
            root = Path(value) / "Epic Games"
            roots[str(root).lower()] = root

    for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        root = Path(f"{drive}:/Program Files/Epic Games")
        roots[str(root).lower()] = root

    return [root for root in roots.values() if root.exists()]


def _existing_engine_installations(
    search_roots: Iterable[Path] | None = None,
) -> list[Path]:
    installs: dict[str, Path] = {}
    roots = list(search_roots) if search_roots is not None else _default_search_roots()
    for root in roots:
        if not root.exists():
            continue
        for candidate in root.glob("UE_*"):
            if candidate.is_dir():
                installs[str(candidate.resolve()).lower()] = candidate.resolve()
    return sorted(installs.values(), key=_engine_sort_key, reverse=True)


def _candidate_binary_paths(
    binary_name: str, search_roots: Iterable[Path] | None = None
) -> list[Path]:
    candidates: list[Path] = []
    for install in _existing_engine_installations(search_roots):
        candidates.append(install / "Engine" / "Binaries" / "Win64" / binary_name)
    return candidates


def _read_windows_product_version(path: Path) -> str | None:
    if os.name != "nt":
        return None

    literal = str(path).replace("'", "''")
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"(Get-Item -LiteralPath '{literal}').VersionInfo.ProductVersion",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    version = result.stdout.strip()
    return version or None


def _build_resolution(path: Path, source: str) -> dict[str, object]:
    version = _read_windows_product_version(path)
    return {
        "available": True,
        "path": _normalize_path(path),
        "source": source,
        "version": version or _extract_engine_version_hint(path),
        "engine_version_hint": _extract_engine_version_hint(path),
    }


def _missing_resolution(binary_name: str, reason: str) -> dict[str, object]:
    return {
        "available": False,
        "path": None,
        "source": "unresolved",
        "version": None,
        "engine_version_hint": None,
        "error": f"{binary_name} not found: {reason}",
    }


def resolve_engine_root(engine_root: str | Path) -> Path:
    """Normalize a UE install root from either the install root or Engine subdir."""
    path = Path(engine_root).expanduser().resolve()
    root = path.parent if path.name.lower() == "engine" else path
    if not root.exists():
        raise RuntimeError(f"Engine root not found: {root}")
    if not (root / "Engine").is_dir():
        raise RuntimeError(f"Engine root must contain an Engine directory: {root}")
    return root


def resolve_binary_from_engine_root(
    binary_name: str,
    engine_root: str | Path,
    required: bool = True,
) -> dict[str, object]:
    """Resolve a UE program binary from a specific engine root."""
    root = resolve_engine_root(engine_root)
    candidate = root / "Engine" / "Binaries" / "Win64" / binary_name
    if candidate.is_file():
        return _build_resolution(candidate, f"engine:{root.name}")
    if required:
        raise RuntimeError(f"{binary_name} not found under engine root: {root}")
    return _missing_resolution(binary_name, f"missing under engine root {root}")
