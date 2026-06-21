# ruff: noqa: F403, F405, E501
from .discovery_base import *  # noqa: F403

# fmt: off
from .discovery_p1 import _candidate_dirs_from_env, _default_windows_install_dirs, _scan_directory  # noqa: E402,E501
from .discovery_p2 import _override_value  # noqa: E402,E501
# fmt: on


def discover_binaries(
    env: Optional[dict[str, str]] = None,
    which: Optional[Callable[[str], Optional[str]]] = None,
    glob_func: Optional[Callable[[str], list[str]]] = None,
    platform_system: Optional[str] = None,
    nsight_path: Optional[str] = None,
) -> dict[str, Any]:
    """Discover available Nsight binaries."""
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    glob_func = glob.glob if glob_func is None else glob_func
    platform_system = platform.system() if platform_system is None else platform_system

    binaries: dict[str, Optional[str]] = {
        "ngfx": None,
        "ngfx_ui": None,
        "ngfx_capture": None,
        "ngfx_replay": None,
    }
    search_roots: list[str] = []
    override = _override_value(env, nsight_path=nsight_path)

    if override:
        override_path = Path(override)
        if override_path.is_file():
            for key, candidates in _BINARY_CANDIDATES.items():
                lowered = {name.lower() for name in candidates}
                if override_path.name.lower() in lowered:
                    binaries[key] = str(override_path.resolve())
                    break
        search_roots.extend(_candidate_dirs_from_env(override))

    for key, candidates in _BINARY_CANDIDATES.items():
        for candidate in candidates:
            resolved = which(candidate)
            if resolved:
                binaries[key] = binaries[key] or str(Path(resolved).resolve())
                search_roots.append(str(Path(resolved).resolve().parent))
                break

    if platform_system == "Windows":
        search_roots.extend(_default_windows_install_dirs(glob_func))

    for directory in _dedupe(search_roots):
        found = _scan_directory(directory)
        for key, value in found.items():
            binaries[key] = binaries[key] or value

    return {
        "binaries": binaries,
        "search_roots": _dedupe(search_roots),
        "env_override": env.get(ENV_VAR, "").strip() or None,
        "cli_override": nsight_path.strip()
        if nsight_path and nsight_path.strip()
        else None,
        "effective_override": override or None,
    }


def _primary_executable(binaries: dict[str, Optional[str]]) -> Optional[str]:
    """Choose the preferred executable path to display."""
    return (
        binaries.get("ngfx")
        or binaries.get("ngfx_capture")
        or binaries.get("ngfx_replay")
    )
